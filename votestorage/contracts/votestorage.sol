// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract VoteStorage {
    struct Vote {
        bytes signature;
        bytes randomNumber;
    }

    Vote[] private votes;

    /// @dev store votes
    function storeVote(bytes memory _signature, bytes memory _randomNumber) public {
        votes.push(Vote(_signature, _randomNumber));
    }

    /// @dev get votes total number
    function getVotesCount() public view returns (uint256) {
        return votes.length;
    }

    /// @dev get vote data
    function getVote(uint256 index) public view returns (bytes memory, bytes memory) {
        require(index < votes.length, "Index out of range");
        Vote memory vote = votes[index];
        return (vote.signature, vote.randomNumber);
    }
}
