import { NextResponse } from 'next/server';
import { FASTAPI_URL } from '@/lib/types';

export async function POST() {
	try {
		const res = await fetch(`${FASTAPI_URL}/generate-all`, {
			method: 'POST',
			cache: 'no-store',
		});
		const data = await res.json();
		return NextResponse.json(data, { status: res.status });
	} catch (error) {
		console.error('Erreur POST /generate-all:', error);
		return NextResponse.json({ error: 'Backend indisponible' }, { status: 502 });
	}
}
