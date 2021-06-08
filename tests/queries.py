create_user = """
mutation createUser(
    $email: String!,
    $username: String!,
    $password1: String!,
    $password2: String!
    ) {
  register(
    email:$email,
    username: $username,
    password1: $password1,
    password2: $password2) {
      success
      errors
  }
}
"""

list_users = """
query {
  users(isActive: true){
    edges {
      node {
        uid
        username
        email
        isActive
        verified
      }
    }
  }
}
"""

list_users_by_email = """
query ($email: String!){
  users(email: $email){
    edges {
      node {
        uid
        username
        isActive
        verified
      }
    }
  }
}

"""
