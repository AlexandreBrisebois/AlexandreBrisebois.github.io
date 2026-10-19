#!/bin/bash

# local/dev.sh
# srvrlss.dev local dev & run suite

# Ensure we're in the repository root
cd "$(dirname "$0")/.." || exit

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load secrets from .env if it exists
if [ -f "local/.env" ]; then
    echo -e "${GREEN}✓ Loading secrets from local/.env${NC}"
    set -a
    . "local/.env"
    set +a
fi

# Detect Python environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Using virtual environment (.venv)${NC}"
    PYTHON_CMD="./.venv/bin/python3"
else
    echo -e "${YELLOW}! No .venv found, using system python3${NC}"
    PYTHON_CMD="python3"
fi

get_lan_ip() {
    local default_iface

    default_iface=$(route get default 2>/dev/null | awk '/interface:/{print $2; exit}')
    if [ -n "$default_iface" ]; then
        ipconfig getifaddr "$default_iface" 2>/dev/null && return 0
    fi

    ipconfig getifaddr en0 2>/dev/null && return 0
    ipconfig getifaddr en1 2>/dev/null && return 0

    return 1
}

show_menu() {
    echo -e "\n${BLUE}--- srvrlss.dev Dev Suite ---${NC}"
    echo "1) Start Hugo Server (Drafts enabled)"
    echo "2) Run Automation: Dry Run (Safe local validation)"
    echo "3) Run Automation: Full (Requires API Key)"
    echo "4) Run Image Generation (Multi-shot)"
    echo "q) Quit"
    echo -n "Select option: "
}

run_automation() {
    mode=$1
    mock_ci=$2
    force_posts=$3

    echo -e "${YELLOW}Running automation mode: $mode (CI Mock: $mock_ci)${NC}"
    
    if [ "$mock_ci" == "true" ]; then
        if [ -z "$GEMINI_API_KEY" ]; then
            echo -e "${RED}Error: GEMINI_API_KEY is not set in environment or local/.env${NC}"
            return
        fi
        export GITHUB_ACTIONS="true"
        export BASE_BRANCH="main"
    fi

    if [ -n "$force_posts" ]; then
        export FORCE_POSTS="$force_posts"
    fi

    $PYTHON_CMD .github/scripts/content_automation.py --mode "$mode"
}

while true; do
    show_menu
    read -r opt
    case $opt in
        1)
            LAN_IP=$(get_lan_ip)
            if [ -n "$LAN_IP" ]; then
                echo -e "${GREEN}Starting Hugo Server on http://${LAN_IP}:1313/${NC}"
                hugo server -D --bind 0.0.0.0 --baseURL "http://${LAN_IP}:1313"
            else
                echo -e "${YELLOW}! Could not detect LAN IP, starting Hugo Server on localhost only${NC}"
                hugo server -D
            fi
            ;;
        2)
            run_automation "pr" "false"
            ;;
        3)
            echo -n "Enter post filename(s) to run (comma-separated, leave blank for git diff): "
            read -r posts
            run_automation "pr" "true" "$posts"
            ;;
        4)
            echo -n "Enter post filename(s) for image generation (comma-separated, leave blank for git diff): "
            read -r posts
            echo -e "${YELLOW}Running image generation...${NC}"
            $PYTHON_CMD local/image_generator.py --posts "$posts"
            ;;
        q)
            echo "Goodbye!"
            break
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
done
