import { NextRequest } from 'next/server';
import { ChatRequest } from '../../../lib/types';

// Define the types for our API
type ChatRequestBody = ChatRequest;

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body: ChatRequestBody = await request.json();

    // Get the authorization header from the incoming request
    const authHeader = request.headers.get('authorization');

    // For now, we'll make a direct call to the backend
    // In a real implementation, you'd want to call your backend API
    const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_API_URL || 'https://todo-web-app-nvu7.onrender.com'}/chat/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
      body: JSON.stringify(body),
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('Backend API error:', errorText);
      return new Response(
        JSON.stringify({
          error: 'Failed to process chat request',
          details: errorText
        }),
        {
          status: backendResponse.status,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    const data = await backendResponse.json();

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('API route error:', error);
    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}