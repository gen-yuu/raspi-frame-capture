import threading
import traceback

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
def init_camera():
    """
    カメラを初期化．既に初期化されている場合はそのままの状態を返す．

    Returns:
        Tuple[str, int]: カメラの初期化状態とHTTPステータスコード
            - "already-initialized" (200): カメラが既に初期化されている
            - "initialized" (201): カメラが初期化された
            - "init-failed" (500): カメラの初期化に失敗
    """
    global camera
    with cam_lock:
        if camera is not None:
            return "already-initialized", 200
        try:
            camera = Camera()
            logger.info(
                "Camera initialized via API",
                extra={
                    "ip": request.remote_addr,
                },
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
def release_camera():
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


@app.get("/capture")
def capture_frame() -> Response | tuple[str, int]:
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
