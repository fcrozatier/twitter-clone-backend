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

# Profile queries

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
      ... on BaseDatedType {
        uid
      }
    }
  }
}"""

my_followers = """query myFollowers(
    $first: Int,
    $skip: Int
) {
  myProfile {
    followers(first: $first, skip: $skip) {
      uid
      email
      username
    }
  }
}"""

my_subs = """query mySubs(
    $first: Int,
    $skip: Int
) {
  myProfile {
    follows(first: $first, skip: $skip) {
      uid
      email
    }
  }
}"""

user_profile = """query userProfile(
    $uid: String!
) {
  userProfile(uid: $uid) {
    uid
    email
    username
    followersCount
    tweets {
      created
      content
    }
  }
}"""

user_followers = """query userFollowers(
    $uid: String!
) {
  userProfile(uid: $uid) {
    followers {
      uid
      email
    }
  }
}"""

user_subs = """query userSubs(
    $uid: String!
) {
  userProfile(uid: $uid) {
    follows {
      uid
      email
    }
  }
}
"""

my_content = """query Content(
  $skip: Int=0,
  $limit: Int=10
) {
  myProfile {
    content(skip: $skip, limit: $limit){
        __typename
      ... on BaseDatedType {
        uid
        created
      }
      ... on LikeableType {
        likes
      }
      ... on TweetType {
        content
      }
      ... on CommentType {
        content
        about {
          __typename
          ... on TweetType {
            content
          }
          ... on ReTweetType {
            tweet {
              content
            }
          }
        }
      }
    }
  }
}
"""

user_content = """query userContent(
  $uid: String!,
  $skip: Int=0,
  $limit: Int=10
) {
  userProfile(uid: $uid) {
    content(skip: $skip, limit: $limit){
      __typename
      ... on BaseDatedType {
        uid
        created
      }
      ... on LikeableType {
        likes
      }
      ... on TweetType {
        content
      }
      ... on CommentType {
        content
        about {
          __typename
          ... on TweetType {
            content
          }
          ... on ReTweetType {
            tweet {
              content
            }
          }
        }
      }
    }
  }
}
"""

my_feed = """query myFeed(
  $skip: Int=0,
  $limit: Int=10
) {
  myFeed(skip: $skip, limit: $limit) {
    __typename
    ... on BaseDatedType {
      uid
      created
    }
    ... on LikeableType {
      likes
    }
    ... on TweetType {
      content
    }
  }
}
"""


# Tweet queries
tweet = """mutation newTweet(
    $content: String!,
    $hashtags: [String!],
){
  tweet(content: $content, hashtags: $hashtags){
      content
      likes
      comments
      retweets
      created
      hashtags {
        tag
        tags
      }
  }
}"""

retweet = """mutation createRetweet(
    $uid: String!
) {
  retweet(uid: $uid){
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
}"""

like = """mutation createLike(
    $uid: String!,
    $type: String!,
) {
  like(uid: $uid, type: $type){
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
}"""

unlike = """mutation DeleteLike(
  $uid: String!,
  $type: String!
) {
  unlike(type: $type, uid: $uid){
    __typename
    ... on BaseDatedType {
        uid
      }
    ... on LikeableType {
      likes
    }
  }
}
"""

comment = """mutation createComment(
    $uid: String!,
    $type: String!
    $content: String!,
) {
  comment(uid: $uid, type: $type, content: $content){
    about {
      __typename
      ... on CommentableType {
        comments
        commentsList {
          content
          created
        }
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

follow = """mutation followUser(
  $uid: String!
) {
  follow(uid: $uid){
    uid
    email
    username
    followersCount
  }
}"""

unfollow = """mutation unFollowUser(
  $uid: String!
) {
  unfollow(uid: $uid){
    uid
    email
    username
    followersCount
  }
}"""
