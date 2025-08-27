@extends('layouts.app')

@section('content')
<div class="container">
  <h1>VAPT Scanner</h1>

  @if ($errors->any())
    <div class="alert alert-danger">
      <ul>@foreach ($errors->all() as $e)<li>{{ $e }}</li>@endforeach</ul>
    </div>
  @endif
  @if (session('status'))
    <div class="alert alert-success">{{ session('status') }}</div>
  @endif

  <form method="post" action="{{ route('vapt.start') }}">
    @csrf
    <div class="mb-3">
      <label class="form-label">Target URL</label>
      <input type="url" name="target_url" class="form-control" required placeholder="https://example.com" value="{{ old('target_url') }}">
    </div>
    <div class="mb-3">
      <label class="form-label">Engine</label>
      <select name="engine" class="form-select">
        <option value="zap">zap</option>
        <option value="nmap">nmap</option>
        <option value="sqlmap">sqlmap</option>
        <option value="wapiti">wapiti</option>
      </select>
    </div>
    <button class="btn btn-primary">Start Scan</button>
  </form>

  <hr>

  <form class="row g-2" method="get" action="{{ route('vapt.get', ['id' => 0]) }}" onsubmit="event.preventDefault(); window.location=this.action.replace('/0','/'+document.getElementById('scanId').value);">
    <div class="col-auto">
      <input id="scanId" type="number" class="form-control" placeholder="Scan ID">
    </div>
    <div class="col-auto">
      <button class="btn btn-secondary">View Scan</button>
    </div>
  </form>
</div>
@endsection