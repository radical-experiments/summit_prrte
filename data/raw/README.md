# Scaling Experiment

## Storing data

After executing an experiment run:

```txt
SID=`ls -tr | grep rp.session | tail -1`
cp ../sbox/$SID/pilot.0000/*.log $SID/
tar cfj $SID.tar.bz2 $SID
mv $SID.tar.bz2 ../data/raw/
rm -r $SID
echo "| $SID | $NODES | $TASKS | passed | prrte |" >> ../data/raw/README.md
git add ../data/raw
git commit -m 'Experiment run '
git pull
git push
```

## Testing

| SID | \#nodes | \#tasks | executor | notes |
|-----|---------|---------|----------|-------|
| rp.session.login3.mturilli1.018442.0011 | 1 | 11 | jsrun | passed |
| rp.session.login3.mturilli1.018442.0012 | 1 | 11 | prrte | missing logs |
| rp.session.login4.mturilli1.018443.0002 | 2 | 22 | prrte | missing logs |
| rp.session.login4.mturilli1.018443.0003 | 2 | 22 | prrte | wrong concurrency |
| rp.session.login4.mturilli1.018444.0000 | 2 | 21 | prrte | passed |
| rp.session.login4.mturilli1.018444.0001 | 128 | 1116 | prrte | wrong concurrency |
| rp.session.login4.mturilli1.018444.0003 | 4 | 42 | passed | prrte |
| rp.session.login4.mturilli1.018444.0004 | 4 | 126 | passed | prrte |
| rp.session.login4.mturilli1.018444.0005 | 4 | 126 | hotfix/prrte events | prrte |


## Experiment

| SID | \#nodes | \#tasks | \#generations | executor | notes |
|-----|---------|---------|----------|-------|
| rp.session.login2.mturilli1.018474.0000 | 128 | TBD | 1 | prrte 1 | passed |
| rp.session.login2.mturilli1.018488.0001 | 128 | TBD | 1 | prrte master | passed |
