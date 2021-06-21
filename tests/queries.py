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

my_profile = """query {
   myProfile {
    email
    username
    followersCount
    tweets {
      created
      content
    }
    retweets {
      likes
      tweet {
        uid
      }
    }
    comments {
      content
    }
    likes {
      __typename
      ... on TweetType {
        uid
      }
      ... on ReTweetType {
        uid
      }
      ... on CommentType {
        uid
      }
    }
  }
}"""

my_followers = """query {
  myFollowers {
    uid
    email
  }
}"""

my_subs = """query {
  mySubs {
    uid
    email
  }
}"""

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

create_like = """mutation createLike(
    $uid: String!,
    $type: String!,
) {
  createLike(uid: $uid, type: $type){
    likeable {
        __typename
      ... on BaseDatedType {
        uid
      }
        likes
      ... on TweetType{
        content
      }
      ... on ReTweetType {
        comments
      }
      ... on CommentType {
        content
      }
    }
  }
}"""

create_comment = """mutation createComment(
    $uid: String!,
    $type: String!
    $content: String!,
) {
  createComment(uid: $uid, type: $type, content: $content){
    commentable {
      __typename
      comments
      commentsList {
        content
        created
      }
      ... on TweetType {
        uid
        likes
      	content
      }
      ... on ReTweetType {
        uid
        likes
        tweet {
          content
        }
      }
    }
  }
}"""

follow_user = """mutation followUser(
  $uid: String!
) {
  followUser(uid: $uid){
    user {
      uid
      email
      username
      followersCount
    }
  }
}"""
