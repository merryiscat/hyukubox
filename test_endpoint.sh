#!/bin/bash

# MCP Endpoint 테스트 스크립트

if [ $# -eq 0 ]; then
    echo "Usage: $0 <endpoint-url>"
    echo "Example: $0 http://123.45.67.89:8000/mcp"
    exit 1
fi

ENDPOINT=$1

echo "============================================"
echo "MCP Endpoint 테스트"
echo "============================================"
echo "Endpoint: $ENDPOINT"
echo ""

# 1. tools/list 테스트
echo "[1/2] tools/list 테스트..."
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}')

if echo "$RESPONSE" | grep -q "search_song"; then
    echo "✓ tools/list 성공"
    echo "$RESPONSE" | grep -o '"name":"[^"]*"' | head -5
else
    echo "✗ tools/list 실패"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

# 2. 실제 툴 호출 테스트
echo "[2/2] search_song 툴 호출 테스트..."
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_song","arguments":{"artist":"IU","title":"Love wins all"}},"id":2}')

if echo "$RESPONSE" | grep -q "곡 정보"; then
    echo "✓ search_song 호출 성공"
    echo "$RESPONSE" | grep -o "곡명: [^\\]*" | head -1
else
    echo "✗ search_song 호출 실패"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

echo "============================================"
echo "모든 테스트 통과!"
echo "============================================"
echo ""
echo "Claude Desktop에서 사용 가능:"
echo "MCP Endpoint: $ENDPOINT"
