export interface Guest {
	id: string;
	name: string;
	tableName: string;
	tableId?: string;
	theme?: string;
	seatNumber?: number;
	/** PDF unique de 3 pages (billet + invitation + QR), servi depuis public/billets/. */
	pdfUrl?: string;
	/** Même PDF hébergé sur Cloudinary. */
	cloudPdfUrl?: string;
	qrData?: string;
	status?: 'pending' | 'generated' | 'uploaded' | 'error';
	checkedIn?: boolean;
	checkedInAt?: string | null;
	createdAt?: string;
}

export interface Table {
	id: string;
	name: string;
	subtitle?: string;
	theme?: string;
	seats: number;
	guests: Guest[];
}

export const FASTAPI_URL =
	process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://127.0.0.1:8001';
