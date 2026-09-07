import { NextResponse } from 'next/server';
import { FASTAPI_URL } from '@/lib/types';

export async function POST(req: Request) {
	try {
		const body = await req.json();
		const guestId = body?.guestId;
		if (!guestId) {
			return NextResponse.json({ error: 'guestId requis' }, { status: 400 });
		}
		const res = await fetch(`${FASTAPI_URL}/generate/${guestId}`, {
			method: 'POST',
			cache: 'no-store',
		});
		const data = await res.json();
		return NextResponse.json(data, { status: res.status });
	} catch (error) {
		console.error('Erreur POST /generate:', error);
		return NextResponse.json({ error: 'Backend indisponible' }, { status: 502 });
	}
}
