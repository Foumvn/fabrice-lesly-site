'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Download, Loader2, ArrowLeft, CheckCircle2 } from 'lucide-react';
import type { Guest } from '@/lib/types';

export default function BilletViewerPage() {
	const params = useParams();
	const guestId = params?.id as string;

	const [guest, setGuest] = useState<Guest | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		if (!guestId) return;
		(async () => {
			try {
				const res = await fetch(`/api/guests/${guestId}`, { cache: 'no-store' });
				if (res.ok) {
					const data = await res.json();
					setGuest(data);
				}
			} catch (err) {
				console.error(err);
			} finally {
				setLoading(false);
			}
		})();
	}, [guestId]);

	if (loading) {
		return (
			<main className="flex min-h-screen items-center justify-center bg-[#0a0a0a] text-white">
				<Loader2 className="h-8 w-8 animate-spin text-white/50" />
			</main>
		);
	}

	if (!guest) {
		return (
			<main className="flex min-h-screen flex-col items-center justify-center bg-[#0a0a0a] px-6 text-white">
				<p className="font-serif text-2xl">Billet introuvable</p>
				<p className="mt-2 text-sm text-white/50">
					Le lien que vous avez utilisé est invalide ou expiré.
				</p>
			</main>
		);
	}

	// PDF unique de l'invité. Cloudinary sert de secours si le fichier local
	// n'a pas encore été publié dans public/billets/.
	const pdfUrl = guest.pdfUrl || guest.cloudPdfUrl || null;
	const presenceUrl = '/presence';

	return (
		<main className="relative flex min-h-screen flex-col items-center bg-[#0a0a0a] px-4 pb-32 pt-12 text-white">
			<div className="w-full max-w-xl text-center">
				<div className="mb-6 flex flex-col items-center">
					<img
						src="/anneaux.png"
						alt="Anneaux de mariage"
						className="w-16 opacity-80 sm:w-20"
					/>
					<h1 className="mt-3 font-serif text-3xl tracking-tight md:text-4xl">
						<span className="italic">Votre billet</span>
					</h1>
					<p className="mt-2 font-mono text-xs uppercase tracking-widest text-white/50">
						{guest.name} — {guest.tableName}
					</p>
				</div>

				{/* Aperçu du PDF */}
				{pdfUrl ? (
					<div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl">
						<iframe
							src={pdfUrl}
							title={`Billet ${guest.name}`}
							className="h-[70vh] w-full bg-white"
						/>
					</div>
				) : (
					<div className="rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl">
						<div className="mb-4 flex justify-center">
							<CheckCircle2 className="h-12 w-12 text-orange-400" />
						</div>
						<p className="font-serif text-2xl">Merci {guest.name} !</p>
						<p className="mt-2 text-sm text-white/60">
							Votre invitation a bien été enregistrée.
						</p>
						<p className="mt-1 text-sm text-white/60">
							Le lien de votre billet personnel vous sera envoyé prochainement.
						</p>
					</div>
				)}

				{/* Actions */}
				<div className="mt-6 flex flex-col items-center gap-3">
					{pdfUrl && (
						<a
							href={pdfUrl}
							download
							className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-orange-400 bg-orange-500/20 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-orange-500/40 active:scale-[0.98]"
						>
							<Download className="h-4 w-4" />
							Télécharger mon billet
						</a>
					)}

					{!guest.checkedIn && (
						<a
							href={presenceUrl}
							className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-white/15 bg-white/10 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-white/20 active:scale-[0.98]"
						>
							Confirmer ma présence
						</a>
					)}

					{guest.checkedIn && (
						<p className="inline-flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-6 py-2 font-mono text-xs uppercase tracking-widest text-green-300">
							<CheckCircle2 className="h-4 w-4" />
							Présence confirmée
						</p>
					)}

					<a
						href="/"
						className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-2.5 font-mono text-xs uppercase tracking-widest text-white/60 transition hover:bg-white/10"
					>
						<ArrowLeft className="h-4 w-4" />
						Retour à l'accueil
					</a>
				</div>
			</div>
		</main>
	);
}
