import json, logging, argparse, datetime, re, os
import pandas as pd

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)
os.makedirs('data_visualizations', exist_ok = True)


def attached_urls(attachments):
    ## attachements is a list, and attachements['data'] is a list, but example never has more than 1 element
    for a in attachments:
        for adata in a['data']:
            if 'external_context' in adata.keys():
                yield adata['external_context']['url']


def parse_posts(posts, outgoing=True):
    l = []
    for post in posts:
        d = {'time': post['timestamp'], 'message': '', 'urls': [], 'outgoing': outgoing}
        d['time'] = datetime.datetime.fromtimestamp(d['time'])
        try:
            if 'data' in post.keys():
                ## it seems like the post data list can only contain one post (though then a dict would have been more likely)
                for postdata in post['data']:
                    if 'post' in postdata.keys():
                        d['message'] = postdata['post']
            if 'attachments' in post.keys():
                for url in attached_urls(post['attachments']):
                    d['urls'].append(url)
        except:
            log.warning("Could not parse posts")
        l.append(d)
    df = pd.DataFrame(l)
    return df

def parse_comments(comments):
    l = []
    for comment in comments:
        d = {'time': comment['timestamp'], 'message': '', 'urls': [], 'group': '', 'outgoing': True}
        d['time'] = datetime.datetime.fromtimestamp(d['time'])
        try:
            if 'data' in comment.keys():
                for comment_data in comment['data']:
                    ## it seems like the comment data list can only contain one comment (though then a dict would have been more likely)
                    if 'comment' in comment_data.keys():
                        comment_data = comment['data'][0]['comment']
                        d['message'] = comment_data['comment']
                        d['group'] = comment_data['group'] if 'group' in comment_data.keys() else ''
            if 'attachments' in comment.keys():
                for url in attached_urls(comment['attachments']):
                    d['urls'].append(url)
        except:
            log.warning("Could not parse comment")
        l.append(d)
    df = pd.DataFrame(l)
    return df



def parse_data(file_path):
    print(os.path.join(file_path, 'comments', 'comments.json'))
    with open(os.path.join(file_path, 'comments', 'comments.json'), 'r') as f:
        comments = json.loads(f.read())['comments']
        comments = parse_comments(comments)

    ## we should check whether people with many posts can also have your_posts_2 etc.
    with open(os.path.join(file_path, 'posts', 'your_posts_1.json'), 'r') as f:
        own_posts = json.loads(f.read())    ## so here they just give a list of posts
        own_posts = parse_posts(own_posts, outgoing=True)

    with open(os.path.join(file_path, 'posts', "other_people's_posts_to_your_timeline.json"), 'r') as f:
        other_posts = json.loads(f.read())['wall_posts_sent_to_you']['activity_log_data']  ## but here they first drown the posts list in dicts
        own_posts = parse_posts(other_posts, outgoing=False)


    print(own_posts)
    print(other_posts)
    print(comments)
    return comments



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The folder with the Facebook data')
    args = parser.parse_args()

    o = parse_data(args.file)