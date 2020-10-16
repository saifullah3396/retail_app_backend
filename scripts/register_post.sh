#curl -X POST -d "@register_post.txt" http://127.0.0.1:8000/api/v1/accounts/register/
curl -H "Content-Type: application/json" --data @register_post.json http://127.0.0.1:8000/api/v1/accounts/register/
