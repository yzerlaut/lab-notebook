update_ip() {
  local IF=en0 SVC="Wi-Fi" HOTSPOT="iPad-Yann"
  local IP=172.20.10.14 MASK=255.255.255.240 GW=172.20.10.1
  local ssid
  ssid=$(ipconfig getsummary "$IF" | awk -F ' SSID : ' '/ SSID : / {print $2}')

  if [[ -z "$ssid" ]]; then
    echo "Not connected to Wi-Fi."; return 1
  elif [[ "$ssid" == "<redacted>" ]]; then
    echo "SSID hidden by macOS. Run once: sudo ipconfig setverbose 1"; return 1
  fi

  if [[ "$ssid" == "$HOTSPOT" ]]; then
    echo "On $ssid: setting static IP $IP"
    sudo networksetup -setmanual "$SVC" "$IP" "$MASK" "$GW"
    sudo networksetup -setdnsservers "$SVC" "$GW"
  else
    echo "On $ssid: switching to DHCP"
    sudo networksetup -setdhcp "$SVC"
    sudo networksetup -setdnsservers "$SVC" empty
  fi

  sleep 2
  echo "Current IP: $(ipconfig getifaddr "$IF")"
}

