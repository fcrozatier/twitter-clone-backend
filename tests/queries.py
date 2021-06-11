# Account queries
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
      token
      errors
  }
}
"""

last_user = """query {
  users (last: 1){
    edges {
      node {
        id,
        uid,
        username,
        email,
      }
    }
  }
}
"""

list_users = """
query {
  users {
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

# Tweet queries
create_tweet = """mutation newTweet(
    $content: String!
){
  createTweet(content: $content){
    tweet {
      content
      likes
      comments
      retweets
      created
    }
  }
}"""

create_retweet = """mutation createRetweet(
    $tweetUid: String!
) {
  createRetweet(tweetUid: $tweetUid){
    retweet {
      uid
      likes
      comments
      created
      tweet {
        uid
        content
        likes
        comments
        retweets
      }
    }
  }
}"""

like_tweet = """mutation createLike(
    $tweetUid: String!
){
  createLike(tweetUid: $tweetUid){
    tweet {
      uid
      content
      likes
      created
    }
  }
}"""

create_comment = """mutation createComment(
    $content: String!,
    $tweetUid: String!
) {
  createComment(content: $content, tweetUid: $tweetUid){
    comment {
      uid
      content
      created
      tweet {
        uid
        content
        likes
        comments
      }
    }
  }
}"""
