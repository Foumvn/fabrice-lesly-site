import { NextResponse } from 'next/server';
import { db } from '@/lib/firebase';
import { collection, getDocs, addDoc, doc, setDoc } from 'firebase/firestore';

export async function GET() {
	try {
		const guestsRef = collection(db, 'guests');
		const snapshot = await getDocs(guestsRef);
		const guests = snapshot.docs.map((doc) => ({
			id: doc.id,
			...(doc.data() as object),
		}));
		return NextResponse.json({ guests, count: guests.length });
	} catch (error) {
		console.error('Erreur GET /api/guests:', error);
		return NextResponse.json({ guests: [], count: 0 }, { status: 500 });
	}
}

export async function POST(req: Request) {
	try {
		const data = await req.json();
		const { id, ...rest } = data;
		const base = { ...rest, createdAt: new Date().toISOString() };
		if (id) {
			await setDoc(doc(db, 'guests', String(id)), base);
			return NextResponse.json({ id, ...base }, { status: 201 });
		}
		const ref = await addDoc(collection(db, 'guests'), base);
		return NextResponse.json({ id: ref.id, ...base }, { status: 201 });
	} catch (error) {
		console.error('Erreur POST /api/guests:', error);
		return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 });
	}
}
