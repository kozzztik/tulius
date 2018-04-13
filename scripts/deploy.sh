#!/bin/sh
# Configure SSH
openssl aes-256-cbc -K $encrypted_45eab4e05705_key -iv $encrypted_45eab4e05705_iv -in scripts/ssh.key.enc -out /tmp/deploy_rsa -d
eval "$(ssh-agent -s)"
chmod 600 /tmp/deploy_rsa
ssh-add /tmp/deploy_rsa

# Download updates
ssh -i /tmp/deploy_rsa travis@tulius.com -p 33023 "cd ~/$TRAVIS_BRANCH && git fetch --all && git reset --hard && git pull --rebase"
echo "Data updated"

# Do after deploy staff
ssh -i /tmp/deploy_rsa travis@tulius.com -p 33023 "cd ~/$TRAVIS_BRANCH && . scripts/on_update.sh"
echo "Finished."