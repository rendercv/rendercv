import { describe, it, expect, vi } from 'vitest';
import { getPreferences, setPreference } from './preferences';

describe('getPreferences', () => {
	it('returns the {key: value} map', async () => {
		const fetchImpl = vi
			.fn()
			.mockResolvedValue(new Response(JSON.stringify({ zoom: '110' }), { status: 200 }));
		const result = await getPreferences(fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith('/api/preferences');
		expect(result).toEqual({ zoom: '110' });
	});
});

describe('setPreference', () => {
	it('PUTs {key, value} and resolves on 204', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
		await setPreference('zoom', '110', fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/preferences',
			expect.objectContaining({ method: 'PUT', body: JSON.stringify({ key: 'zoom', value: '110' }) })
		);
	});

	it('throws on an unexpected status', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 500 }));
		await expect(setPreference('zoom', '110', fetchImpl)).rejects.toThrow();
	});
});
