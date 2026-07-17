[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$walkthrough = $PSScriptRoot
$repository = Split-Path $walkthrough -Parent
$musicDirectory = Join-Path $walkthrough "music"
$musicSource = Join-Path $musicDirectory "quiet-systems.mp3"
$musicBed = Join-Path $musicDirectory "quiet-systems-bed.m4a"
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

    & $ffmpeg -loglevel error -y -i $musicSource -map 0:a:0 `
        -af "atempo=0.9045,apad=pad_dur=1,afade=t=in:st=0:d=2,afade=t=out:st=156:d=4,loudnorm=I=-25:TP=-8:LRA=5" `
        -t 160 -ar 48000 -c:a aac -b:a 128k `
        -metadata title="Quiet Systems — walkthrough mix" `
        -metadata artist="irresistiblewebapps8080" `
        -metadata comment="User-supplied Suno track, duration-fitted and level-normalized for the walkthrough" `
        $musicBed
    if ($LASTEXITCODE -ne 0) { throw "Quiet Systems mix preparation failed." }

    & $ffmpeg -loglevel error -y -i $videoOnly -i $musicBed `
        -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest `
        -metadata title="Arrivia evidence walkthrough" `
        $output
    if ($LASTEXITCODE -ne 0) { throw "Video/music mux failed." }
} finally {
    Pop-Location
    if (Test-Path -LiteralPath $videoOnly) {
        Remove-Item -LiteralPath $videoOnly -Force
    }
    if (Test-Path -LiteralPath $musicBed) {
        Remove-Item -LiteralPath $musicBed -Force
    }
}

Write-Host "Rendered $output with Quiet Systems."
