use App\Http\Controllers\VaptController;

Route::get('/vapt', [VaptController::class, 'index'])->name('vapt.index');
Route::post('/vapt/scan', [VaptController::class, 'startScan'])->name('vapt.start');
Route::get('/vapt/scan/{id}', [VaptController::class, 'getScan'])->name('vapt.get');