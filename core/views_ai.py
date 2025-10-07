
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import AIChatHistory
from .groq_inference import query_groq_api
import uuid
import pprint
import traceback

def clean_message_content(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and 'text' in part:
                texts.append(str(part['text']))
            elif isinstance(part, str):
                texts.append(part)
            else:
                texts.append(str(part))
        return " ".join(texts)
    elif isinstance(content, dict):
        if 'text' in content:
            return str(content['text'])
        return str(content)
    else:
        return str(content)

def clean_message_history(messages):
    cleaned = []
    for msg in messages:
        cleaned.append({
            "role": msg.get("role"),
            "content": clean_message_content(msg.get("content"))
        })
    return cleaned

class CrackItAIChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

        assistant_name = request.session.get('assistant_name', 'Crack_it AI Assistant')
        new_name = request.data.get("set_name")
        if new_name:
            assistant_name = new_name
            request.session['assistant_name'] = assistant_name

        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        history, created = AIChatHistory.objects.get_or_create(
            user=request.user,
            conversation_id=conversation_id,
            defaults={'messages': []}
        )

        cleaned_user_message = clean_message_content(user_message)
        if not history.messages or history.messages[-1].get("content") != cleaned_user_message:
            history.messages.append({"role": "user", "content": cleaned_user_message})

        cleaned_messages = clean_message_history(history.messages)

        # Debug: print cleaned messages right before sending to Groq
        print("DEBUG: Cleaned messages being sent to Groq API:")
        pprint.pprint(cleaned_messages)

        try:
            answer = query_groq_api(cleaned_messages)
            cleaned_answer = clean_message_content(answer)
            history.messages.append({"role": "assistant", "content": cleaned_answer})
            history.save()

            return Response({
                "answer": cleaned_answer,
                "assistant_name": assistant_name,
                "conversation_id": conversation_id,
            })

        except Exception as e:
            traceback.print_exc()  # Print full traceback for debugging
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAIChatHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        try:
            chat = AIChatHistory.objects.get(id=chat_id, user=request.user)
            chat.delete()
            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
        except AIChatHistory.DoesNotExist:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
