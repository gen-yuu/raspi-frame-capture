import threading
import traceback
from typing import Tuple, Union

import cv2
from flask import Flask, Response, request  # type: ignore

from src.system.camera import Camera
from src.utils.logger import setup_logger

logger = setup_logger("frame-capture")
app = Flask(__name__)
cam_lock = threading.Lock()
camera = None


# --- Camera Control Endpoints ---
@app.post("/camera/init")
def init_camera() -> Tuple[str, int]:
    """
    カメラを初期化し、解像度を動的に設定できる。
    例:
        POST /camera/init?width=640&height=480
        POST /camera/init          (JSON) {"width":1280,"height":720}
    """
    global camera
    with cam_lock:
        if camera is not None:
            return "already-initialized", 200

        # --- パラメータ取得 ---
        default_w, default_h = 1280, 720
        payload = request.get_json(silent=True) or {}
        width = int(request.args.get("width", payload.get("width", default_w)))
        height = int(request.args.get("height", payload.get("height", default_h)))

        try:
            camera = Camera(width=width, height=height)
            logger.info(
                "Camera initialized via API",
                extra={"ip": request.remote_addr},
            )
            return "initialized", 201
        except Exception as e:
            logger.error(
                "Camera initialization failed",
                extra={
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            return "init-failed", 500


@app.post("/camera/release")
def release_camera() -> Tuple[str, int]:
    """
    カメラリソースを解放．既に解放されている場合はそのままの状態を返す．

    Returns:
        Tuple[str, int]: カメラの解放状態とHTTPステータスコード
            - "already-released" (200): カメラが既に解放されている
            - "released" (200): カメラが解放された
            - "release-failed" (500): カメラの解放に失敗
    """
    global camera
    with cam_lock:
        if camera is None:
            return "already-released", 200
        try:
            camera.release()
            camera = None
            logger.info(
                "Camera released via API",
                extra={
                    "ip": request.remote_addr,
                },
            )
            return "released", 200
        except Exception as e:
            logger.error(
                "Camera release failed",
                extra={
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            return "release-failed", 500


# --- Frame Capture Endpoint ---
@app.get("/capture")
def capture_frame() -> Union[Response, Tuple[str, int]]:
    """
    カメラからフレームを 1 枚取得し、JPEG 画像として返します。

    Returns:
        Response | tuple[str, int]
            - Response (200) : 正常終了時の JPEG バイナリ
            - ("camera-not-initialized", 409) : カメラが初期化されていない
            - ("no-frame", 500) : フレームの取得に失敗
            - ("encode-failed", 500) : JPEG へのエンコードに失敗
    """

    global camera
    if camera is None:
        return "camera-not-initialized", 409

    logger.info(
        "Capture request",
        extra={
            "ip": request.remote_addr,
        },
    )
    frame = camera.get_frame()
    if frame is None:
        logger.error("Failed to get frame from camera")
        return "no-frame", 500

    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        return "encode-failed", 500

    return Response(buffer.tobytes(), mimetype="image/jpeg")


# --- Health Check Endpoint ---
@app.get("/health")
def health() -> Tuple[str, int]:
    return "ok", 200


if __name__ == "__main__":
    try:
        logger.info("Starting Pi Camera API Server")
        app.run(host="0.0.0.0", port=8080, debug=False)
    finally:
        # Pi shutdown / SIGTERM 時の安全解放
        with cam_lock:
            if camera:
                camera.release()
                logger.info("Camera released on shutdown")
