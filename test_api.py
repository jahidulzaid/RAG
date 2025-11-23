"""Simple test script to verify API functionality."""

import requests
import time

API_BASE = "http://localhost:8000"

def test_status():
    """Test status endpoint."""
    print("Testing /api/status...")
    try:
        response = requests.get(f"{API_BASE}/api/status")
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"   Vectorstore: {'Initialized' if data['vectorstore_initialized'] else 'Not initialized'}")
        print(f"   Model: {data['model_name']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query():
    """Test query endpoint."""
    print("\nTesting /api/query...")
    try:
        response = requests.post(
            f"{API_BASE}/api/query",
            json={
                "question": "What is RAG?",
                "maintain_history": True
            }
        )
        data = response.json()
        print(f"✅ Query successful")
        print(f"   Session ID: {data['session_id']}")
        print(f"   Answer: {data['answer'][:100]}...")
        print(f"   Sources: {len(data['sources'])} document(s)")
        
        # Test follow-up question
        print("\nTesting follow-up question...")
        response2 = requests.post(
            f"{API_BASE}/api/query",
            json={
                "question": "What are its benefits?",
                "session_id": data['session_id'],
                "maintain_history": True
            }
        )
        data2 = response2.json()
        print(f"✅ Follow-up successful")
        print(f"   Answer: {data2['answer'][:100]}...")
        
        return data['session_id']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_history(session_id):
    """Test history endpoint."""
    if not session_id:
        print("\n⏭️  Skipping history test (no session)")
        return
    
    print(f"\nTesting /api/history/{session_id}...")
    try:
        response = requests.get(f"{API_BASE}/api/history/{session_id}")
        data = response.json()
        print(f"✅ History retrieved")
        print(f"   Exchanges: {len(data['history'])}")
        for i, item in enumerate(data['history'], 1):
            print(f"   {i}. Q: {item['question']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ingest():
    """Test ingest endpoint."""
    print("\nTesting /api/ingest...")
    try:
        response = requests.post(
            f"{API_BASE}/api/ingest",
            json={"path": "./data"}
        )
        data = response.json()
        if data['success']:
            print(f"✅ Ingest successful")
            print(f"   Documents processed: {data['documents_processed']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"⚠️  {data['message']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("RAG API Test Suite")
    print("=" * 50)
    print(f"\nAPI Base: {API_BASE}")
    print("Make sure the server is running!")
    print("=" * 50)
    
    # Give user time to check
    time.sleep(1)
    
    # Run tests
    results = []
    
    results.append(("Status", test_status()))
    results.append(("Ingest", test_ingest()))
    
    session_id = test_query()
    results.append(("Query", session_id is not None))
    results.append(("History", test_history(session_id)))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:15} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    print("=" * 50)

if __name__ == "__main__":
    main()
