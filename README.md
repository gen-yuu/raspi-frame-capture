# RaspiFrameCapture

## Deplyment

```bash
# 1. リポジトリクローン
git clone https://github.com/your-org/face-frame-capture.git
cd face-frame-capture

# 2. 初回セットアップ（root権限）
chmod +x setup.sh
./setup.sh

# 3. systemd登録
sudo cp deploy/systemd/frame-capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now frame-capture.service

# 4. 動作確認
curl http://localhost:8080/camera/init
curl http://localhost:8080/capture --output test.jpg

# 5. ログ確認
journalctl -u frame-capture.service -f
tail -f /var/log/frame_capture.log | jq
```
