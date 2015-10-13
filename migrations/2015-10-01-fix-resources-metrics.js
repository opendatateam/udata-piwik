var result = db.dataset.update(
    {$where: 'this.resources && !Array.isArray(this.resources)'},
    {$set: {resources: []}},
    {multi: true}
);

print('Fixed ' + result.nModified + ' datasets');
