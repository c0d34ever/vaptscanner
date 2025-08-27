@extends('layouts.app')

@section('content')
<div class="container">
  <h1>Scan #{{ $scan['id'] ?? '' }}</h1>
  <p><strong>Target:</strong> {{ $scan['target_url'] ?? '' }}</p>
  <p><strong>Engine:</strong> {{ $scan['engine'] ?? '' }}</p>
  <p><strong>Status:</strong> {{ $scan['status'] ?? '' }}</p>
  <p><strong>Started:</strong> {{ $scan['start_time'] ?? '' }}</p>
  <p><strong>Ended:</strong> {{ $scan['end_time'] ?? '' }}</p>

  <h3>Findings</h3>
  @php $alerts = $scan['report_json'] ?? []; @endphp
  @if (is_array($alerts) && count($alerts))
    <ul>
      @foreach ($alerts as $a)
        <li>
          <strong>{{ $a['alert'] ?? ($a['name'] ?? 'Finding') }}</strong>
          ({{ $a['risk'] ?? ($a['severity'] ?? 'Info') }})
          <div>URL: {{ $a['url'] ?? '' }}</div>
          <div>{{ $a['description'] ?? '' }}</div>
        </li>
      @endforeach
    </ul>
  @else
    <p>No findings yet or scan still running.</p>
  @endif

  <h3>Raw JSON</h3>
  <pre style="white-space: pre-wrap">{{ json_encode($scan, JSON_PRETTY_PRINT) }}</pre>
</div>
@endsection