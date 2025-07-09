# RaspiFrameCapture

## Deplyment

```bash
# 1. リポジトリクローン
git clone https://github.com/your-org/face-frame-capture.git
cd face-frame-capture

# 2. 初回セットアップ
chmod +x setup.sh
./setup.sh

# 3. systemd登録
sudo cp deploy/systemd/frame-capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now frame-capture.service
sudo systemctl status frame-capture.service

# 4. ヘルスチェック
curl -s http://localhost:8080/health

# 5. カメラ起動確認
curl -X POST http://localhost:8080/camera/init
curl -o frame.jpg http://localhost:8080/capture
curl -X POST http://localhost:8080/camera/release

# 5. ログ確認
journalctl -u frame-capture.service -f
```

### Restart Service

```shell
# 現在の状態を確認
sudo systemctl status frame-capture.service

# サービス再起動（最新versionを読み込み）
sudo systemctl restart frame-capture.service

# 再起動が成功したか確認
sudo systemctl status frame-capture.service
```
