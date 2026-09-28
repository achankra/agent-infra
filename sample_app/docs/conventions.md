# Team conventions

- Credentials are read from the environment at call time. A literal token in
  source is a policy failure, not a style problem.
- Hot paths index into structures. Linear scans over dictionaries are rejected
  in review.
- Every public function has a type annotation.
- Log lines never include credential material.
