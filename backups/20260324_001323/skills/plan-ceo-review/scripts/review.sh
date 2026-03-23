#!/bin/bash
# Plan CEO Review - Interactive CLI

echo "=============================================="
echo "  CEO Plan Review - OpenClaw Edition"
echo "=============================================="
echo ""
echo "This review follows the gstack methodology:"
echo "  1. Scope Challenge (is this the right problem?)"
echo "  2. Mode Selection (how ambitious should we be?)"
echo "  3. Failure Mode Analysis (what can go wrong?)"
echo "  4. Recommendations (what should we do?)"
echo ""

echo "Select review mode:"
echo "  A) SCOPE EXPANSION   - Dream big, push scope UP"
echo "  B) SELECTIVE EXPANSION - Baseline + cherry-pick"
echo "  C) HOLD SCOPE       - Rigorous, make bulletproof"
echo "  D) SCOPE REDUCTION  - Minimum viable, cut excess"
echo ""
read -p "Choose (A/B/C/D): " mode

case $mode in
  A|a) echo "🎯 Mode: SCOPE EXPANSION - Let's dream big!" ;;
  B|b) echo "🎯 Mode: SELECTIVE EXPANSION - Baseline + choices" ;;
  C|c) echo "🎯 Mode: HOLD SCOPE - Rigorous review" ;;
  D|d) echo "🎯 Mode: SCOPE REDUCTION - Minimum viable" ;;
  *) echo "Invalid selection" ; exit 1 ;;
esac

echo ""
echo "Now describe the plan you want to review:"
echo "(What are you building? What's the goal?)"
read -p "> " plan_description

echo ""
echo "What problem does this solve?"
read -p "> " problem

echo ""
echo "What's the expected outcome?"
read -p "> " outcome

echo ""
echo "=============================================="
echo "Review Session Started"
echo "=============================================="
echo ""
echo "Mode: $mode"
echo "Plan: $plan_description"
echo "Problem: $problem"
echo "Outcome: $outcome"
echo ""
echo "Tell this to Harvey 🤖 to begin your review."
