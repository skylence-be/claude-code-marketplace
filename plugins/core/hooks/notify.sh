#!/usr/bin/env bash
payload=$(cat)
event=$(echo "$payload" | jq -r '.hook_event_name // "Unknown"')

case "$event" in
  PreCompact)
    trigger=$(echo "$payload" | jq -r '.matcher // "auto"')
    title="Claude Code"
    message="$trigger compaction starting. Switch to sonnet[1m] if not already."
    ;;
  PostCompact)
    trigger=$(echo "$payload" | jq -r '.compaction_trigger // "auto"')
    title="Claude Code"
    message="Compaction done ($trigger). Context reset."
    ;;
  Stop)
    title="Claude Code"
    message="Turn complete."
    ;;
  StopFailure)
    error=$(echo "$payload" | jq -r '.error_type // "unknown"')
    title="Claude Code - Error"
    message="Stopped with error: $error"
    ;;
  TeammateIdle)
    agent=$(echo "$payload" | jq -r '.agent_type // "agent"')
    title="Claude Code - Team"
    message="Teammate going idle: $agent"
    ;;
  Notification)
    type=$(echo "$payload" | jq -r '.notification_type // ""')
    title="Claude Code"
    message="Idle: Claude is waiting for input."
    [[ "$type" != "idle_prompt" ]] && exit 0
    ;;
  *)
    exit 0
    ;;
esac

if command -v osascript &>/dev/null; then
  osascript -e "display notification \"$message\" with title \"$title\""
elif command -v powershell.exe &>/dev/null; then
  powershell.exe -NonInteractive -Command "
    Add-Type -AssemblyName System.Windows.Forms
    \$n = New-Object System.Windows.Forms.NotifyIcon
    \$n.Icon = [System.Drawing.SystemIcons]::Information
    \$n.BalloonTipTitle = '$title'
    \$n.BalloonTipText = '$message'
    \$n.Visible = \$true
    \$n.ShowBalloonTip(8000)
    Start-Sleep -Milliseconds 8500
    \$n.Dispose()
  " &
elif command -v notify-send &>/dev/null; then
  notify-send "$title" "$message"
fi
