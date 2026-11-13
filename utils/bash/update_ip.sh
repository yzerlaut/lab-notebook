# ---------------------------------------------------------------------------
# update_ip: on the iPad hotspot, give this computer a static IP (so that the
# iPad always finds it at the same address, e.g. for ipad_sync.sh), and go
# back to DHCP on any other Wi-Fi network.
#   macOS: networksetup on the "Wi-Fi" service (needs sudo)
#   Linux: NetworkManager (nmcli), on the connection profile of the hotspot
#          only; the other Wi-Fi profiles are left untouched (they use DHCP)
# Works in bash and zsh.
# ---------------------------------------------------------------------------

update_ip() {
  local HOTSPOT="iPad-Yann"
  local IP=172.20.10.14 MASK=255.255.255.240 PREFIX=28 GW=172.20.10.1
  if [[ "$(uname)" == Darwin ]]; then
    _update_ip_macos
  else
    _update_ip_linux
  fi
}

_update_ip_macos() {
  local IF=en0 SVC="Wi-Fi" ssid
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

_update_ip_linux() {
  command -v nmcli >/dev/null 2>&1 || { echo "nmcli (NetworkManager) not found."; return 1; }
  local ssid con dev
  ssid=$(nmcli -t -f active,ssid dev wifi 2>/dev/null | sed -n 's/^yes://p' | head -n 1)

  if [[ -z "$ssid" ]]; then
    echo "Not connected to Wi-Fi."; return 1
  elif [[ "$ssid" != "$HOTSPOT" ]]; then
    echo "On $ssid: nothing to do (DHCP; the static IP is set on the $HOTSPOT profile only)"
  else
    # active connection profile on that Wi-Fi network
    con=$(nmcli -t -f NAME,TYPE,DEVICE con show --active | awk -F: '$2 ~ /wireless/ {print $1; exit}')
    dev=$(nmcli -t -f NAME,TYPE,DEVICE con show --active | awk -F: '$2 ~ /wireless/ {print $3; exit}')
    if [[ "$(nmcli -g ipv4.addresses con show "$con")" == "$IP/$PREFIX" ]]; then
      echo "On $ssid: static IP $IP already set"
    else
      echo "On $ssid: setting static IP $IP (profile \"$con\")"
      sudo nmcli con mod "$con" ipv4.method manual ipv4.addresses "$IP/$PREFIX" \
          ipv4.gateway "$GW" ipv4.dns "$GW" &&
        sudo nmcli con up "$con" >/dev/null
    fi
  fi

  sleep 2
  dev=${dev:-$(nmcli -t -f DEVICE,TYPE dev | awk -F: '$2 == "wifi" {print $1; exit}')}
  echo "Current IP: $(ip -4 -o addr show dev "$dev" 2>/dev/null | awk '{print $4}' | cut -d/ -f1)"
}
