#!/bin/sh
# Configure SSH
openssl aes-256-cbc -K $encrypted_45eab4e05705_key -iv $encrypted_45eab4e05705_iv -in scripts/ssh.key.enc -out /tmp/deploy_rsa -d
eval "$(ssh-agent -s)"
chmod 600 /tmp/deploy_rsa
ssh-add /tmp/deploy_rsa

# Configure git remote
git remote add deploy "ssh://travis@tulius.com:33023/home/travis/$TRAVIS_BRANCH"
git config user.name "Travis CI"
git config user.email "travis@mywebsite.com"

# Push
git status # debug
git push deploy
echo "Git Push Done"

# Do after deploy staff
ssh -i /tmp/deploy_rsa -o UserKnownHostsFile=/dev/null travis@tulius.com 'cd /home/travis/$TRAVIS_BRANCH; echo hello; scripts/on_update.sh'
