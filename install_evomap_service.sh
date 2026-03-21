#!/bin/bash
# Install EvoMap heartbeat as a launchd service

PLIST_NAME="com.fhjtech.evomap.heartbeat.plist"
PLIST_SRC="/Users/fhjtech/.openclaw/workspace/$PLIST_NAME"
PLIST_DEST="/Users/fhjtech/Library/LaunchAgents/$PLIST_NAME"

echo "Installing EvoMap heartbeat service..."

# Copy plist to LaunchAgents
cp "$PLIST_SRC" "$PLIST_DEST"
if [ $? -eq 0 ]; then
    echo "✓ Plist copied to $PLIST_DEST"
else
    echo "✗ Failed to copy plist"
    exit 1
fi

# Load the service
launchctl load "$PLIST_DEST"
if [ $? -eq 0 ]; then
    echo "✓ Service loaded successfully"
else
    echo "✗ Failed to load service"
    exit 1
fi

# Start the service (it should start automatically due to RunAtLoad)
launchctl start "$PLIST_NAME"
if [ $? -eq 0 ]; then
    echo "✓ Service started"
else
    echo "⚠ Could not start service (might already be running)"
fi

echo ""
echo "Service installed. To check status:"
echo "  launchctl list | grep evomap"
echo "  tail -f /Users/fhjtech/.openclaw/workspace/evomap_heartbeat_launchd.log"
echo ""
echo "To uninstall:"
echo "  launchctl unload $PLIST_DEST"
echo "  rm $PLIST_DEST"