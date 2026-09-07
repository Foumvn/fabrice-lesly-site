import { NextResponse } from 'next/server';
import { db } from '@/lib/firebase';
import { doc, getDoc, updateDoc, deleteDoc } from 'firebase/firestore';

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
	const { id } = await params;
	try {
		const ref = doc(db, 'guests', id);
		const snap = await getDoc(ref);
		if (!snap.exists()) {
			return NextResponse.json({ error: 'Invité introuvable' }, { status: 404 });
		}
		return NextResponse.json({ id, ...(snap.data() as object) });
	} catch (error) {
		console.error('Erreur GET /api/guests/[id]:', error);
		return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 });
	}
}

export async function PUT(req: Request, { params }: { params: Promise<{ id: string }> }) {
	const { id } = await params;
	try {
		const data = await req.json();
		const ref = doc(db, 'guests', id);
		await updateDoc(ref, data);
		return NextResponse.json({ id, ...data });
	} catch (error) {
		console.error('Erreur PUT /api/guests/[id]:', error);
		return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 });
	}
}

export async function DELETE(_req: Request, { params }: { params: Promise<{ id: string }> }) {
	const { id } = await params;
	try {
		const ref = doc(db, 'guests', id);
		await deleteDoc(ref);
		return NextResponse.json({ success: true, id });
	} catch (error) {
		console.error('Erreur DELETE /api/guests/[id]:', error);
		return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 });
	}
}
