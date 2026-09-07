'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
	Plus,
	Trash2,
	Download,
	Loader2,
	RefreshCw,
	Upload,
	Sparkles,
} from 'lucide-react';
import { toast, Toaster } from 'sonner';
import { EVENT_TABLES, SEATS_PER_TABLE } from '@/lib/tables';
import type { Guest } from '@/lib/types';

export default function AdminBilletsPage() {
	const [guests, setGuests] = useState<Guest[]>([]);
	const [loading, setLoading] = useState(true);
	const [generating, setGenerating] = useState(false);
	const [showAddForm, setShowAddForm] = useState(false);

	// Formulaire
	const [newName, setNewName] = useState('');
	const [newTable, setNewTable] = useState(EVENT_TABLES[0]?.name || '');

	const loadGuests = useCallback(async () => {
		try {
			const res = await fetch('/api/guests', { cache: 'no-store' });
			const data = await res.json();
			setGuests(data.guests || []);
		} catch (err) {
			console.error(err);
			toast.error('Impossible de charger les invités');
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		loadGuests();
	}, [loadGuests]);

	const addGuest = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!newName.trim()) return;
		try {
			const res = await fetch('/api/guests', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: newName.trim(),
					tableName: newTable,
					status: 'pending',
					checkedIn: false,
					checkedInAt: null,
				}),
			});
			if (res.ok) {
				toast.success(`Invité "${newName}" ajouté`);
				setNewName('');
				setShowAddForm(false);
				loadGuests();
			} else {
				toast.error('Erreur lors de l\'ajout');
			}
		} catch (err) {
			console.error(err);
			toast.error('Erreur réseau');
		}
	};

	const deleteGuest = async (id: string) => {
		try {
			await fetch(`/api/guests/${id}`, { method: 'DELETE' });
			toast.success('Invité supprimé');
			loadGuests();
		} catch (err) {
			console.error(err);
			toast.error('Erreur lors de la suppression');
		}
	};

	const generateAll = async () => {
		setGenerating(true);
		try {
			const res = await fetch('/api/billets/generate-all', { method: 'POST' });
			const data = await res.json();
			if (res.ok) {
				toast.success(`${data.uploaded} billets générés sur ${data.total}`);
			} else {
				toast.error(data.error || 'Échec de la génération');
			}
			loadGuests();
		} catch (err) {
			console.error(err);
			toast.error('Backend FastAPI indisponible');
		} finally {
			setGenerating(false);
		}
	};

	const generateOne = async (guest: Guest) => {
		try {
			const res = await fetch('/api/billets/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ guestId: guest.id }),
			});
			const data = await res.json();
			if (res.ok) {
				toast.success(`Billet généré pour ${guest.name}`);
				loadGuests();
			} else {
				toast.error(data.error || 'Erreur');
			}
		} catch (err) {
			console.error(err);
			toast.error('Backend indisponible');
		}
	};

	const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const text = await file.text();
		const lines = text.split('\n').filter((l) => l.trim());
		let imported = 0;
		for (const line of lines) {
			const [name, tableName] = line.split(',').map((s) => s.trim());
			if (!name || !tableName) continue;
			await fetch('/api/guests', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name,
					tableName,
					status: 'pending',
					checkedIn: false,
					checkedInAt: null,
				}),
			});
			imported++;
		}
		toast.success(`${imported} invités importés`);
		loadGuests();
		e.target.value = '';
	};

	// Regrouper les invités par table
	const grouped = guests.reduce<Record<string, Guest[]>>((acc, g) => {
		const table = g.tableName || 'Sans table';
		(acc[table] = acc[table] || []).push(g);
		return acc;
	}, {});

	const pdfHref = (g: Guest) => g.pdfUrl || g.cloudPdfUrl || null;
	const generatedCount = guests.filter((g) => pdfHref(g)).length;

	return (
		<main className="relative min-h-screen bg-[#0a0a0a] px-4 pb-32 pt-16 text-white">
			<Toaster position="top-center" theme="dark" />

			<div className="mx-auto w-full max-w-5xl">
				{/* Header */}
				<div className="mb-6 flex flex-col items-center gap-4 text-center">
					<img
						src="/anneaux.png"
						alt="Anneaux de mariage"
						className="w-16 opacity-80 sm:w-20"
					/>
					<div>
						<h1 className="font-serif text-4xl tracking-tight md:text-5xl">
							<span className="italic">Admin</span> billetterie
						</h1>
						<p className="mt-2 font-mono text-xs uppercase tracking-widest text-white/50">
							Mariage de Fabrice et Leslie — gestion des invités
						</p>
					</div>
				</div>

				{/* Statistiques */}
				<div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
					{[['Tables', EVENT_TABLES.length], ['Invités', guests.length], ['Billets générés', generatedCount], ['Places/table', SEATS_PER_TABLE]].map(
						([label, value]) => (
							<div
								key={label as string}
								className="rounded-3xl border border-white/10 bg-white/5 p-5 text-center backdrop-blur-xl"
							>
								<div className="font-serif text-3xl">{value}</div>
								<div className="mt-1 font-mono text-[11px] uppercase tracking-widest text-white/50">
									{label}
								</div>
							</div>
						)
					)}
				</div>

				{/* Actions */}
				<div className="mb-8 flex flex-wrap items-center justify-center gap-3">
					<button
						onClick={generateAll}
						disabled={generating}
						className="inline-flex items-center gap-2 rounded-full border border-orange-400 bg-orange-500/20 px-6 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-orange-500/40 active:scale-[0.98] disabled:opacity-50"
					>
						{generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
						Générer tous les billets
					</button>

					<button
						onClick={() => setShowAddForm((v) => !v)}
						className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-6 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-white/20 active:scale-[0.98]"
					>
						<Plus className="h-4 w-4" />
						Ajouter un invité
					</button>

					<label className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-white/15 bg-white/10 px-6 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-white/20 active:scale-[0.98]">
						<Upload className="h-4 w-4" />
						Importer CSV
						<input type="file" accept=".csv,.txt" className="hidden" onChange={handleImportCSV} />
					</label>

					<button
						onClick={loadGuests}
						className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-white/20 active:scale-[0.98]"
					>
						<RefreshCw className="h-4 w-4" />
					</button>
				</div>

				{/* Formulaire d'ajout */}
				{showAddForm && (
					<form
						onSubmit={addGuest}
						className="mx-auto mb-8 max-w-md rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
					>
						<h3 className="mb-4 font-serif text-xl">Ajouter un invité</h3>
						<div className="space-y-4">
							<div>
								<label className="mb-1 block font-mono text-[11px] uppercase tracking-widest text-white/50">
									Nom &amp; prénom
								</label>
								<input
									value={newName}
									onChange={(e) => setNewName(e.target.value)}
									placeholder="Ex: Rostand Essima"
									className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 outline-none transition focus:border-orange-400"
								/>
							</div>
							<div>
								<label className="mb-1 block font-mono text-[11px] uppercase tracking-widest text-white/50">
									Table
								</label>
								<select
									value={newTable}
									onChange={(e) => setNewTable(e.target.value)}
									className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-orange-400"
								>
									{EVENT_TABLES.map((t) => (
										<option key={t.name + t.subtitle} value={`${t.name} - ${t.subtitle}`} className="bg-black">
											{t.name} - {t.subtitle}
										</option>
									))}
								</select>
							</div>
							<button
								type="submit"
								className="w-full rounded-full border border-orange-400 bg-orange-500/20 py-3 font-mono text-sm uppercase tracking-widest transition hover:bg-orange-500/40 active:scale-[0.98]"
							>
								Ajouter
							</button>
						</div>
					</form>
				)}

				{/* Liste des tables et invités */}
				{loading ? (
					<div className="flex justify-center py-20">
						<Loader2 className="h-8 w-8 animate-spin text-white/50" />
					</div>
				) : (
					<div className="space-y-4">
						{Object.keys(grouped).length === 0 && (
							<p className="py-20 text-center text-white/40">
								Aucun invité. Ajoutez-en ou importez un CSV.
							</p>
						)}

						{Object.entries(grouped).map(([tableName, tableGuests]) => (
							<div
								key={tableName}
								className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl"
							>
								<div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
									<div>
										<h3 className="font-serif text-xl">{tableName}</h3>
										<p className="font-mono text-[11px] uppercase tracking-widest text-white/50">
											{tableGuests.length}/{SEATS_PER_TABLE} places
										</p>
									</div>
								</div>
								<div className="divide-y divide-white/5">
									{tableGuests.map((guest) => (
										<div key={guest.id} className="flex items-center justify-between px-6 py-3">
											<div className="flex items-center gap-3">
												<div className="flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 font-mono text-xs">
													{guest.name.charAt(0).toUpperCase()}
												</div>
												<span className="text-sm">{guest.name}</span>
												{pdfHref(guest) && (
													<span className="rounded-full bg-green-500/20 px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest text-green-300">
														✓ généré
													</span>
												)}
											</div>
											<div className="flex items-center gap-2">
												{pdfHref(guest) && (
													<a
														href={pdfHref(guest)!}
														target="_blank"
														rel="noopener noreferrer"
														className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 transition hover:bg-white/20"
													>
														<Download className="h-4 w-4" />
													</a>
												)}
												<button
													onClick={() => generateOne(guest)}
													className="rounded-full border border-white/10 bg-white/5 px-3 py-1 font-mono text-[11px] uppercase tracking-widest transition hover:bg-white/20"
												>
													Générer
												</button>
												<button
													onClick={() => deleteGuest(guest.id)}
													className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-red-500/30 bg-red-500/10 text-red-400 transition hover:bg-red-500/30"
												>
													<Trash2 className="h-4 w-4" />
												</button>
											</div>
										</div>
									))}
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</main>
	);
}
