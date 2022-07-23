/**
 * http://usejsdoc.org/
 */

// Node 1st option.
process.argv.splice(1, 0, '--inspect-brk');
// Node 2nd option is this script file.
// Node 3rd option.
process.argv.push('--runInBand');
// Node 4th option.
process.argv.push(__dirname + '/stringutil.test.js');
// Node options more...

console.log(process.argv);

// Run jest command.
debugger;
require('jest/bin/jest.js');
