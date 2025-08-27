<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class VaptController extends Controller
{
    public function index()
    {
        return view('vapt', [
            'apiBase' => config('services.vapt.base'),
            'apiKey'  => config('services.vapt.key'),
        ]);
    }

    public function startScan(Request $request)
    {
        $validated = $request->validate([
            'target_url' => 'required|url',
            'engine'     => 'required|in:zap,nmap,sqlmap,wapiti',
        ]);

        $resp = Http::withHeaders([
            'X-API-Key' => config('services.vapt.key'),
        ])->post(rtrim(config('services.vapt.base'), '/').'/api/scans/create/', [
            'target_url' => (string) $validated['target_url'],
            'engine'     => (string) $validated['engine'],
            'options'    => null,
        ]);

        if (!$resp->ok()) {
            return back()->withErrors(['api' => 'Failed to start scan: '.$resp->body()])->withInput();
        }

        $data = $resp->json();
        return redirect()->route('vapt.get', ['id' => $data['id'] ?? null])
            ->with('status', 'Scan started');
    }

    public function getScan($id)
    {
        $resp = Http::withHeaders([
            'X-API-Key' => config('services.vapt.key'),
        ])->get(rtrim(config('services.vapt.base'), '/')."/api/scans/{$id}/");

        if (!$resp->ok()) {
            return back()->withErrors(['api' => 'Failed to fetch scan: '.$resp->body()]);
        }

        return view('vapt_result', ['scan' => $resp->json()]);
    }
}