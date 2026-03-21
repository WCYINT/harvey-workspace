#!/usr/bin/env python3
"""
Full integration test for Havery's email-learning system
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_client import HaveryEmailClient
from learning_integration import LearningEmailIntegrator

def test_email_sending():
    """Test sending email via SMTP"""
    print("=" * 60)
    print("Test 1: Email Sending")
    print("=" * 60)
    
    client = HaveryEmailClient()
    
    # Send test email
    success = client.send_email(
        to_address="iharvey@agentmail.to",
        subject="Havery Email Integration Test - Full System Test",
        body="""This is a test email from the full integration test suite.

If you receive this, the SMTP sending functionality is working correctly.

Test details:
- Server: smtp.agentmail.to:465
- SSL/TLS: Enabled
- Integration: Python email client

This test is part of Havery's self-improvement system integration.
"""
    )
    
    if success:
        print("✅ Email sent successfully!")
        print("   Check your inbox at iharvey@agentmail.to")
    else:
        print("❌ Failed to send email")
    
    return success

def test_feedback_parsing():
    """Test parsing structured feedback emails"""
    print("\n" + "=" * 60)
    print("Test 2: Feedback Parsing")
    print("=" * 60)
    
    client = HaveryEmailClient()
    
    # Test structured feedback
    structured_feedback = """Category: correction
Priority: high
Area: config

The email integration should send acknowledgment emails when feedback is received.

Suggested: Implement acknowledgment email system in learning_integration.py"""
    
    parsed = client.parse_feedback_email(structured_feedback)
    
    if parsed:
        print("✅ Structured feedback parsed successfully")
        print(f"   Category: {parsed.get('category')}")
        print(f"   Priority: {parsed.get('priority')}")
        print(f"   Area: {parsed.get('area')}")
        print(f"   Summary: {parsed.get('summary', 'N/A')[:50]}...")
    else:
        print("❌ Failed to parse structured feedback")
    
    # Test unstructured feedback (should return None)
    unstructured = "Hey, fix this thing. It's not working right."
    parsed_unstructured = client.parse_feedback_email(unstructured)
    
    if parsed_unstructured is None:
        print("✅ Unstructured feedback correctly identified as non-feedback")
    else:
        print("❌ Unstructured feedback incorrectly parsed as feedback")
    
    return parsed is not None

def _remove_test_entry(filepath):
    """Remove test entry from file (cleanup)"""
    try:
        content = Path(filepath).read_text()
        lines = content.split('\n')
        
        # Find and remove test entry
        new_lines = []
        skip = False
        for line in lines:
            if line.startswith('## [LRN-') and 'feature' in line:
                skip = True
            elif skip and line.startswith('## ['):
                skip = False
            
            if not skip:
                new_lines.append(line)
        
        # Write back cleaned content
        Path(filepath).write_text('\n'.join(new_lines))
        print("   Test entry cleaned up")
        
    except Exception as e:
        print(f"   Warning: Failed to clean up test entry: {e}")

def test_learning_creation():
    """Test creating learning entries from email data"""
    print("\n" + "=" * 60)
    print("Test 3: Learning Creation")
    print("=" * 60)
    
    integrator = LearningEmailIntegrator()
    
    # Test data
    test_email_data = {
        'category': 'feature',
        'priority': 'medium',
        'area': 'integration',
        'summary': 'Add email notification for new feedback received',
        'details': 'When a user sends feedback via email, the system should send an automatic acknowledgment email.',
        'suggested_action': 'Implement acknowledgment email in learning_integration.py',
        'from': 'iharvey@agentmail.to',
        'subject': 'Feature request: Acknowledgment emails'
    }
    
    # Create learning entry
    filepath = integrator.create_learning_from_email(test_email_data)
    
    if filepath and Path(filepath).exists():
        print("✅ Learning entry created successfully")
        print(f"   File: {filepath}")
        
        # Read back to verify
        content = Path(filepath).read_text()
        if "LRN-" in content and "feature" in content:
            print("✅ Learning entry contains correct data")
        else:
            print("❌ Learning entry missing expected data")
        
        # Clean up test entry (remove from file)
        _remove_test_entry(filepath)
        
    else:
        print("❌ Failed to create learning entry")
    
    return filepath is not None

def _remove_test_entry(self, filepath):
    """Remove test entry from file (cleanup)"""
    try:
        content = Path(filepath).read_text()
        lines = content.split('\n')
        
        # Find and remove test entry
        new_lines = []
        skip = False
        for line in lines:
            if line.startswith('## [LRN-') and 'feature' in line:
                skip = True
            elif skip and line.startswith('## ['):
                skip = False
            
            if not skip:
                new_lines.append(line)
        
        # Write back cleaned content
        Path(filepath).write_text('\n'.join(new_lines))
        print("   Test entry cleaned up")
        
    except Exception as e:
        print(f"   Warning: Failed to clean up test entry: {e}")

def test_report_generation():
    """Test daily report generation"""
    print("\n" + "=" * 60)
    print("Test 4: Report Generation")
    print("=" * 60)
    
    integrator = LearningEmailIntegrator()
    
    # Generate report
    report = integrator.email_client.generate_daily_report(str(integrator.learnings_dir))
    
    if report and len(report) > 100:
        print("✅ Daily report generated successfully")
        print(f"   Report length: {len(report)} characters")
        print(f"   Contains summary: {'Summary' in report}")
        print(f"   Contains file list: {'.md' in report}")
    else:
        print("❌ Failed to generate report")
    
    return report is not None and len(report) > 100

def test_full_workflow():
    """Test complete workflow: email → parsing → learning → notification"""
    print("\n" + "=" * 60)
    print("Test 5: Complete Workflow Simulation")
    print("=" * 60)
    
    # Simulate receiving feedback email
    print("Simulating feedback email reception...")
    
    feedback_email = {
        'body': """Category: knowledge
Priority: medium
Area: email

The email integration system should include error handling for SMTP connection failures.

Suggested: Add retry logic and fallback servers in email_client.py""",
        'from': 'iharvey@agentmail.to',
        'subject': 'Knowledge: Error handling in email integration'
    }
    
    # Parse feedback
    client = HaveryEmailClient()
    parsed = client.parse_feedback_email(feedback_email['body'])
    
    if not parsed:
        print("❌ Failed to parse feedback in workflow test")
        return False
    
    print("✅ Feedback parsed")
    
    # Create learning
    integrator = LearningEmailIntegrator()
    parsed['from'] = feedback_email['from']
    parsed['subject'] = feedback_email['subject']
    
    filepath = integrator.create_learning_from_email(parsed)
    
    if not filepath:
        print("❌ Failed to create learning in workflow test")
        return False
    
    print("✅ Learning created")
    print(f"   Learning file: {filepath}")
    
    # Verify learning was created
    if Path(filepath).exists():
        content = Path(filepath).read_text()
        if "knowledge" in content and "email" in content:
            print("✅ Learning content verified")
        else:
            print("❌ Learning content incorrect")
    
    # Clean up
    self._remove_test_entry(filepath)
    
    print("✅ Complete workflow test passed")
    return True

def main():
    """Run all integration tests"""
    print("Havery Email-Learning Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Email Sending", test_email_sending),
        ("Feedback Parsing", test_feedback_parsing),
        ("Learning Creation", test_learning_creation),
        ("Report Generation", test_report_generation),
        ("Complete Workflow", test_full_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Email integration is ready.")
        print("\nNext steps:")
        print("1. Integrate with self-improving-agent skill")
        print("2. Set up periodic monitoring (cron/OpenClaw cron)")
        print("3. Test with real feedback emails")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Review logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)