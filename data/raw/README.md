# Scaling Experiment

## Storing data

After executing an experiment run:

```txt
SID = `ls -tr rp.session.* | tail -1`
cp ../sbox/$SID/pilot.0000/*.log $SID/
tar cfv $SID.tar.bz2 $SID
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
