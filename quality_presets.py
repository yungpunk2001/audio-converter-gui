# -*- coding: utf-8 -*-
"""
Mapeo de formatos y parámetros de calidad.
Filosofía: por defecto priorizar transparencia y evitar pérdidas adicionales.
- Si el destino es sin pérdida (WAV/FLAC/ALAC) usar formatos sin pérdida.
- Si el destino es con pérdida, usar presets recomendados de alta calidad.
- SOXR para resampling de alta calidad si se solicita.
"""
import os
import json
import subprocess
from pathlib import Path

# ---------------------------
# Caché de Metadatos
# ---------------------------

class MetadataCache:
    """
    Caché simple para evitar llamadas repetidas a ffprobe para el mismo archivo.
    Reduce de 3+ llamadas a 1 por archivo.
    """
    def __init__(self):
        self._cache = {}
    
    def get_or_probe(self, ffprobe: str, fpath: str) -> dict:
        """Obtiene metadatos del caché o los obtiene con ffprobe"""
        if fpath not in self._cache:
            self._cache[fpath] = self._probe_all(ffprobe, fpath)
        return self._cache[fpath]
    
    def _probe_all(self, ffprobe: str, fpath: str) -> dict:
        """Una sola llamada a ffprobe para obtener todos los metadatos necesarios"""
        cmd = [
            ffprobe, "-v", "error",
            "-show_entries", "stream:format",
            "-of", "json", fpath
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            return {}
        try:
            return json.loads(p.stdout)
        except:
            return {}
    
    def get_stream_info(self, ffprobe: str, fpath: str) -> dict:
        """Obtiene info del primer stream de audio"""
        data = self.get_or_probe(ffprobe, fpath)
        if "streams" in data and data["streams"]:
            return data["streams"][0]
        return {}
    
    def get_duration(self, ffprobe: str, fpath: str) -> float:
        """Obtiene duración del formato"""
        data = self.get_or_probe(ffprobe, fpath)
        try:
            return float(data.get("format", {}).get("duration", 0))
        except:
            return 0.0
    
    def clear(self):
        """Limpia el caché (útil si se procesan muchos archivos)"""
        self._cache.clear()

# Instancia global del caché
_metadata_cache = MetadataCache()

SUPPORTED_FORMATS_DISPLAY = [
    "WAV (PCM)",
    "FLAC (sin pérdida)",
    "ALAC m4a (sin pérdida)",
    "MP3 (LAME)",
    "AAC m4a",
    "Opus",
    "Ogg Vorbis"
]

DISPLAY_TO_KEY = {
    "WAV (PCM)": "wav",
    "FLAC (sin pérdida)": "flac",
    "ALAC m4a (sin pérdida)": "alac",
    "MP3 (LAME)": "mp3",
    "AAC m4a": "aac",
    "Opus": "opus",
    "Ogg Vorbis": "vorbis"
}

EXT_FOR_FORMAT = {
    "wav": ".wav",
    "flac": ".flac",
    "alac": ".m4a",
    "mp3": ".mp3",
    "aac": ".m4a",
    "opus": ".opus",
    "vorbis": ".ogg",
}

def _format_is_lossy(codec: str) -> bool:
    return codec in {"mp3","aac","opus","vorbis","wma","mp2","ac3","eac3"}

def _duration_seconds(ffprobe: str, fpath: str) -> float:
    """Obtiene duración usando caché"""
    return _metadata_cache.get_duration(ffprobe, fpath)
    
def _src_bitrate_kbps(ffprobe: str, fpath: str) -> int:
    """Obtiene bitrate de origen usando caché"""
    info = _metadata_cache.get_stream_info(ffprobe, fpath)
    br = int(info.get("bit_rate") or 0)
    if br <= 0:
        # VBR: estima por tamaño/tiempo
        dur = _duration_seconds(ffprobe, fpath)
        if dur > 0:
            try:
                size_b = Path(fpath).stat().st_size
                br = int((size_b * 8) / dur)  # bps
            except:
                br = 0
    return max(0, br // 1000)  # kbps

_MP3_CBR_SET = [32,40,48,56,64,80,96,112,128,160,192,224,256,320]

def _round_up_mp3_cbr(kbps: int) -> int:
    for v in _MP3_CBR_SET:
        if kbps <= v:
            return v
    return 320

def _kbps_to_vorbis_q(kbps: int) -> int:
    # tabla aproximada 44.1/48 kHz
    # q5≈160, q6≈192, q7≈224, q8≈256, q9≈320, q10≈500
    if kbps >= 420: return 10
    if kbps >= 300: return 9
    if kbps >= 250: return 8
    if kbps >= 210: return 7
    if kbps >= 180: return 6
    return 5

def _match_policy_for_lossy(ffprobe: str, in_file: str, target_codec: str) -> dict:
    """Devuelve {'mode':'cbr'/'vbr','kbps':int,'vorbis_q':int} según origen. Usa caché."""
    info = _metadata_cache.get_stream_info(ffprobe, in_file)
    src_codec = (info.get("codec_name") or "").lower()
    if not _format_is_lossy(src_codec):
        return {}

    src_kbps = _src_bitrate_kbps(ffprobe, in_file)

    if target_codec == "mp3":
        # iguala a CBR hacia arriba, máx 320
        return {"mode":"cbr", "kbps": min(320, _round_up_mp3_cbr(max(96, src_kbps)))}

    if target_codec == "aac":
        # AAC nativo: hasta 320k razonable
        return {"mode":"cbr", "kbps": min(320, max(96, src_kbps))}

    if target_codec == "opus":
        # Opus efectivo; tope práctico 256k
        return {"mode":"cbr", "kbps": min(256, max(96, src_kbps))}

    if target_codec == "vorbis":
        # Vorbis trabaja mejor en -q
        return {"mode":"vorbis_q", "vorbis_q": _kbps_to_vorbis_q(src_kbps)}

    return {}

def _probe(ffprobe: str, fpath: str, entries: str, select: str = "a:0") -> dict:
    cmd = [
        ffprobe, "-v", "error",
        "-select_streams", select,
        "-show_entries", entries,
        "-of", "json",
        fpath
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {}
    try:
        return json.loads(p.stdout)
    except:
        return {}

def _stream_info(ffprobe: str, fpath: str) -> dict:
    """Obtiene info del stream usando caché"""
    return _metadata_cache.get_stream_info(ffprobe, fpath)

def can_stream_copy(in_f: str, out_f: str, ffprobe: str, target_codec_key: str, params: dict) -> bool:
    """
    Permite copiar sin recodificar si:
    - El contenedor y codec destino coinciden con el origen.
    - No se solicitan cambios de sample rate o canales.
    """
    info = _stream_info(ffprobe, in_f)
    if not info:
        return False

    src_codec = info.get("codec_name", "")
    src_sr = int(info.get("sample_rate", 0) or 0)
    src_ch = int(info.get("channels", 0) or 0)

    # Only if no custom changes requested
    if params.get("mode") == "custom":
        if params.get("samplerate", 0) not in (0, src_sr):
            return False
        if params.get("channels", 0) not in (0, src_ch):
            return False

    # Container check by extension
    _, dst_ext = os.path.splitext(out_f.lower())
    desired_ext = EXT_FOR_FORMAT[target_codec_key]
    if dst_ext != desired_ext:
        return False

    # Codec match
    key_to_codec = {
        "wav": ["pcm_s16le", "pcm_s24le", "pcm_f32le", "pcm_s32le"],
        "flac": ["flac"],
        "alac": ["alac"],
        "mp3": ["mp3"],
        "aac": ["aac"],
        "opus": ["opus"],
        "vorbis": ["vorbis"]
    }
    if target_codec_key in ("wav", "flac", "alac"):
        return src_codec in key_to_codec[target_codec_key]
    if target_codec_key == "mp3":
        return src_codec == "mp3"
    if target_codec_key == "aac":
        return src_codec in ("aac",)
    if target_codec_key == "opus":
        return src_codec == "opus"
    if target_codec_key == "vorbis":
        return src_codec in ("vorbis", "libvorbis")
    return False

def _soxr_filter(use_soxr: bool) -> list:
    if use_soxr:
        # High precision, passband, linear phase. Dither triangular.
        return ["-af", "aresample=resampler=soxr:precision=33:dither_method=triangular"]
    return []

def _format_sample_opts_lossless(fmt_key: str, ffprobe: str, in_file: str) -> list:
    """Opciones de formato para codecs lossless. Usa caché."""
    info = _metadata_cache.get_stream_info(ffprobe, in_file)
    src_fmt = (info.get("sample_fmt") or "").lower()

    if fmt_key == "flac":
        # FLAC acepta s16 o s32 (internamente empaqueta a 24 si procede)
        if any(t in src_fmt for t in ("s32", "s24", "fltp", "flt", "dbl")):
            return ["-sample_fmt", "s32"]
        else:
            return ["-sample_fmt", "s16"]

    if fmt_key == "alac":
        # ALAC requiere formatos PLANARES: s16p o s32p
        if any(t in src_fmt for t in ("s32", "s24", "fltp", "flt", "dbl")):
            return ["-sample_fmt", "s32p"]
        else:
            return ["-sample_fmt", "s16p"]

    return []

def _wav_codec_for_source(ffprobe: str, in_file: str) -> list:
    """Selecciona codec WAV según origen. Usa caché."""
    info = _metadata_cache.get_stream_info(ffprobe, in_file)
    src_fmt = (info.get("sample_fmt") or "").lower()
    if any(t in src_fmt for t in ("fltp", "flt", "dbl")):
        return ["-c:a", "pcm_f32le"]
    if "s32" in src_fmt:
        return ["-c:a", "pcm_s32le"]
    return ["-c:a", "pcm_s24le"]

def build_codec_args(fmt_key: str, params: dict, ffprobe: str, in_file: str) -> tuple[list, str]:
    """
    Devuelve (args, ext) para ffmpeg según formato y parámetros.
    """
    mode = params.get("mode", "max")
    use_soxr = params.get("use_soxr", True if mode=="custom" else True)
    samplerate = int(params.get("samplerate", 0))
    channels = int(params.get("channels", 0))

    args = []

    # Resampling / channels
    if use_soxr:
        args += _soxr_filter(True)
    if samplerate > 0:
        args += ["-ar", str(samplerate)]
    if channels > 0:
        args += ["-ac", str(channels)]

    if fmt_key == "wav":
        args += _wav_codec_for_source(ffprobe, in_file)
        return args, ".wav"

    if fmt_key == "flac":
        args += ["-c:a", "flac", "-compression_level", "8"]
        args += _format_sample_opts_lossless(fmt_key, ffprobe, in_file)
        return args, ".flac"

    if fmt_key == "alac":
        args += ["-c:a", "alac"]
        args += _format_sample_opts_lossless(fmt_key, ffprobe, in_file)
        args += ["-movflags", "use_metadata_tags"]
        return args, ".m4a"

    if fmt_key == "mp3":
        match = _match_policy_for_lossy(ffprobe, in_file, "mp3")
        if mode == "max":
            if match:  # origen con pérdida
                args += ["-c:a","libmp3lame","-b:a", f"{match['kbps']}k"]
            else:      # origen sin pérdida → máximo
                args += ["-c:a","libmp3lame","-b:a","320k"]
        else:
            vbr_q = int(params.get("vbr_q", 0))
            br = int(params.get("bitrate_k", 320))
            if 0 <= vbr_q <= 9:
                args += ["-c:a","libmp3lame","-q:a",str(vbr_q)]
            else:
                args += ["-c:a","libmp3lame","-b:a", f"{br}k"]
        return args, ".mp3"

    if fmt_key == "aac":
        match = _match_policy_for_lossy(ffprobe, in_file, "aac")
        if mode == "max":
            if match:
                args += ["-c:a","aac","-b:a", f"{match['kbps']}k"]
            else:
                args += ["-c:a","aac","-b:a","320k"]      # máximo práctico AAC LC
        else:
            br = int(params.get("bitrate_k", 256))
            args += ["-c:a","aac","-b:a", f"{br}k"]
        args += ["-movflags","use_metadata_tags"]
        return args, ".m4a"

    if fmt_key == "opus":
        match = _match_policy_for_lossy(ffprobe, in_file, "opus")
        if mode == "max":
            if match:
                args += ["-c:a","libopus","-b:a", f"{match['kbps']}k","-vbr","on","-compression_level","10","-application","audio"]
            else:
                args += ["-c:a","libopus","-b:a","510k","-vbr","on","-compression_level","10","-application","audio"]  # tope Opus
        else:
            br = int(params.get("bitrate_k", 192))
            args += ["-c:a","libopus","-b:a", f"{br}k","-vbr","on","-compression_level","10","-application","audio"]
        return args, ".opus"

    if fmt_key == "vorbis":
        match = _match_policy_for_lossy(ffprobe, in_file, "vorbis")
        if mode == "max":
            if match and match.get("mode") == "vorbis_q":
                args += ["-c:a","libvorbis","-q:a", str(match["vorbis_q"])]
            else:
                args += ["-c:a","libvorbis","-q:a","10"]  # máximo (-q 10)
        else:
            vbr_q = int(params.get("vbr_q", 7))
            if 0 <= vbr_q <= 10:
                args += ["-c:a","libvorbis","-q:a", str(vbr_q)]
            else:
                br = int(params.get("bitrate_k", 256))
                args += ["-c:a","libvorbis","-b:a", f"{br}k"]
        return args, ".ogg"

    return ["-c:a", "copy"], EXT_FOR_FORMAT.get(fmt_key, ".out")

def supports_cover(fmt_key: str) -> bool:
    # mp3 (ID3 APIC), m4a/aac/alac (atoms), flac (PICTURE)
    return fmt_key in ("mp3", "aac", "alac", "flac")
