#!/bin/bash

echo "=============================="
echo " TOR CONTROL PASSWORD ROTATE "
echo "=============================="

# تحقق من الصلاحيات
if [[ $EUID -ne 0 ]]; then
  echo "[-] شغل السكربت بصلاحية root"
  exit 1
fi

# توليد كلمة مرور جديدة قوية
NEW_PASSWORD=$(openssl rand -base64 18)
NEW_HASH=$(tor --hash-password "$NEW_PASSWORD" | tail -n 1)

echo "[+] New password generated"

# نسخ احتياطي
cp /etc/tor/torrc /etc/tor/torrc.bak.$(date +%s)

# حذف الإعدادات القديمة
sed -i '/ControlPort/d' /etc/tor/torrc
sed -i '/HashedControlPassword/d' /etc/tor/torrc
sed -i '/CookieAuthentication/d' /etc/tor/torrc

# إضافة الإعدادات الجديدة
cat <<EOF >> /etc/tor/torrc

### AUTO ROTATE ###
ControlPort 9051
HashedControlPassword $NEW_HASH
CookieAuthentication 0
EOF

# إعادة تشغيل Tor
echo "[+] Restarting Tor..."
systemctl restart tor
sleep 3

# تحقق من الحالة
systemctl is-active --quiet tor && echo "[✓] Tor is running" || echo "[✗] Tor failed"

# حفظ كلمة المرور الجديدة
PASS_FILE="/root/tor_control_password.txt"
echo "Tor Control Password: $NEW_PASSWORD" > "$PASS_FILE"
chmod 600 "$PASS_FILE"

# اختبار المصادقة
echo "[+] Testing authentication..."
echo -e "AUTHENTICATE \"$NEW_PASSWORD\"\nQUIT" | nc 127.0.0.1 9051 && echo "[✓] AUTH OK"

echo ""
echo "🔥 PASSWORD CHANGED SUCCESSFULLY 🔥"
echo "Saved at: $PASS_FILE"
