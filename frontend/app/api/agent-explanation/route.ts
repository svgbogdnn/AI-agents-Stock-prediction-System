import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agent_id, agent_report, ticker } = body;

    if (!agent_id || !agent_report || !ticker) {
      return NextResponse.json(
        { error: 'agent_id, agent_report, and ticker are required' },
        { status: 400 }
      );
    }

    // Call Python backend for agent explanation
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    
    const response = await fetch(`${pythonBackendUrl}/agent-explanation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ agent_id, agent_report, ticker }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', errorText);
      throw new Error(`Backend returned ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Error in /api/agent-explanation:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate agent explanation',
        details: error.message 
      },
      { status: 500 }
    );
  }
}

