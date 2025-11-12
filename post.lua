-- post.lua
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
-- For simple test, a single row; wrk will issue repeated requests.
wrk.body = '[[5.1, 3.5, 1.4, 0.2]]'
