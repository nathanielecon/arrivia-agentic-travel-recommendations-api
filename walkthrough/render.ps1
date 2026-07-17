[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$walkthrough = $PSScriptRoot
$repository = Split-Path $walkthrough -Parent
$musicDirectory = Join-Path $walkthrough "music"
$music = Join-Path $musicDirectory "ambient-bed.m4a"
$videoOnly = Join-Path $walkthrough "arrivia-walkthrough.video-only.mp4"
$output = Join-Path $walkthrough "arrivia-walkthrough.mp4"

if ($env:FFMPEG_PATH) {
    $candidate = $env:FFMPEG_PATH
    if (Test-Path -LiteralPath $candidate -PathType Container) {
        $ffmpeg = Join-Path $candidate "ffmpeg.exe"
    } else {
        $ffmpeg = $candidate
    }
} else {
    $ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
}
$ffmpegDirectory = Split-Path $ffmpeg -Parent
$env:FFMPEG_PATH = $ffmpeg
$env:FFPROBE_PATH = Join-Path $ffmpegDirectory "ffprobe.exe"
$env:PATH = "$ffmpegDirectory;C:\Windows\System32;$env:PATH"

New-Item -ItemType Directory -Force -Path $musicDirectory | Out-Null

Push-Location $repository
try {
    & npx --yes hyperframes@0.7.60 lint walkthrough
    if ($LASTEXITCODE -ne 0) { throw "HyperFrames lint failed." }
    & npx --yes hyperframes@0.7.60 check walkthrough
    if ($LASTEXITCODE -ne 0) { throw "HyperFrames check failed." }
    & npx --yes hyperframes@0.7.60 snapshot walkthrough --at 0,5,50,95,150,155
    if ($LASTEXITCODE -ne 0) { throw "HyperFrames snapshot failed." }
    & npx --yes hyperframes@0.7.60 render walkthrough -o $videoOnly --fps 1 --quality draft --workers 4 --strict --crf 30
    if ($LASTEXITCODE -ne 0) { throw "HyperFrames render failed." }

    $chords = @(
        "aevalsrc=0.045*(sin(2*PI*130.8128*t)+sin(2*PI*164.8138*t)+sin(2*PI*195.9977*t)+sin(2*PI*246.9417*t)):s=48000:d=40.75",
        "aevalsrc=0.045*(sin(2*PI*110*t)+sin(2*PI*130.8128*t)+sin(2*PI*164.8138*t)+sin(2*PI*195.9977*t)):s=48000:d=40.75",
        "aevalsrc=0.045*(sin(2*PI*87.3071*t)+sin(2*PI*110*t)+sin(2*PI*130.8128*t)+sin(2*PI*164.8138*t)):s=48000:d=40.75",
        "aevalsrc=0.045*(sin(2*PI*97.9989*t)+sin(2*PI*123.4708*t)+sin(2*PI*146.8324*t)+sin(2*PI*220*t)):s=48000:d=40.75"
    )
    & $ffmpeg -loglevel error -y `
        -f lavfi -i $chords[0] `
        -f lavfi -i $chords[1] `
        -f lavfi -i $chords[2] `
        -f lavfi -i $chords[3] `
        -filter_complex "[0:a][1:a]acrossfade=d=1:c1=tri:c2=tri[x1];[x1][2:a]acrossfade=d=1:c1=tri:c2=tri[x2];[x2][3:a]acrossfade=d=1:c1=tri:c2=tri,aformat=channel_layouts=stereo,lowpass=f=1800,tremolo=f=0.10:d=0.18,aecho=0.8:0.35:1200:0.18,afade=t=in:st=0:d=3,afade=t=out:st=156:d=4,volume=0.55,loudnorm=I=-25:TP=-8:LRA=4[a]" `
        -map "[a]" -t 160 -ar 48000 -c:a aac -b:a 128k `
        -metadata title="Arrivia ambient evidence bed" `
        -metadata comment="Original procedural instrumental; no external samples" `
        $music
    if ($LASTEXITCODE -ne 0) { throw "Ambient music generation failed." }

    & $ffmpeg -loglevel error -y -i $videoOnly -i $music `
        -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest `
        -metadata title="Arrivia evidence walkthrough" `
        $output
    if ($LASTEXITCODE -ne 0) { throw "Video/music mux failed." }
} finally {
    Pop-Location
    if (Test-Path -LiteralPath $videoOnly) {
        Remove-Item -LiteralPath $videoOnly -Force
    }
}

Write-Host "Rendered $output with original ambient music."
