from MomentoAI import MomentoAIClient
client = MomentoAIClient(
    api_key="public-access",
    api_url="https://momento-ai-1-42230574747.asia-south1.run.app",
    supabase_url="https://gwkssmbaszagcuzqrlsj.supabase.co",
    supabase_service_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3a3NzbWJhc3phZ2N1enFybHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTAyNjY0NywiZXhwIjoyMDY2NjAyNjQ3fQ.t57lqDxoN3Jrp-3krOjSvMkidMouyYDAf3keYG9r3OY",
    supabase_bucket="face-images"
)
print(client.search_face("trees", event_id="event1", business_id="business1"))
