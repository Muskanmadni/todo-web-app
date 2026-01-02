from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlmodel import Session
from ..models.conversation import Conversation, ConversationBase
from ..models.message import Message
from ..services.conversation_service import ConversationService
from ..db.session import get_session
from fastapi.security import HTTPBearer


router = APIRouter()
security = HTTPBearer()


@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    context_data: dict = {},
    session: Session = Depends(get_session),
    # In a real implementation, you'd get the user from the token
    # user: User = Depends(get_current_user)
):
    """
    Create a new conversation
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")

    conversation = ConversationService.create_conversation(session, mock_user_id, context_data)
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=Message)
def send_message(
    conversation_id: UUID,
    content: str,
    sender_type: str,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Send a message in a specific conversation
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")

    message = ConversationService.add_message_to_conversation(
        session, conversation_id, mock_user_id, sender_type, content
    )
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return message


@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
def get_conversation_messages(
    conversation_id: UUID,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Get all messages for a specific conversation
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")

    messages = ConversationService.get_messages_for_conversation(session, conversation_id, mock_user_id)
    if not messages:  # If conversation doesn't exist or user doesn't have access
        # Check if the conversation exists at all to determine the error
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, mock_user_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return messages


@router.get("/conversations/{conversation_id}/context", response_model=dict)
def get_conversation_context(
    conversation_id: UUID,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Get the context data for a specific conversation
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")

    context_data = ConversationService.get_conversation_context(session, conversation_id, mock_user_id)
    if context_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or no context available")

    return context_data


@router.put("/conversations/{conversation_id}/context", response_model=Conversation)
def update_conversation_context(
    conversation_id: UUID,
    context_data: dict,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Update the context data for a specific conversation
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")

    updated_conversation = ConversationService.update_conversation_context_with_new_data(
        session, conversation_id, mock_user_id, context_data
    )
    if not updated_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return updated_conversation