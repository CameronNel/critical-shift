using System.Collections.Generic;

namespace CriticalShift.Application
{
    // One bounded stream per authenticated connection. No transport or persistence implementation.
    internal sealed class CommandReceipts
    {
        private readonly int _capacity;
        private readonly Dictionary<long, Receipt> _retained = new Dictionary<long, Receipt>();
        private readonly Queue<long> _order = new Queue<long>();

        internal CommandReceipts(int capacity) { _capacity = capacity; }
        internal long LastSequence { get; private set; }
        internal int Count => _retained.Count;

        internal InteractionReply? Check(InteractionCommand command)
        {
            if (command.Sequence <= LastSequence)
            {
                if (!_retained.TryGetValue(command.Sequence, out var previous))
                    return new InteractionReply(InteractionStatus.TooOld, false);
                return previous.Command.SamePayload(command)
                    ? previous.Reply.AsReplay()
                    : new InteractionReply(InteractionStatus.PayloadMismatch, false);
            }
            // Subtraction is safe: admitted sequences and LastSequence are non-negative.
            return command.Sequence - LastSequence == 1
                ? null : new InteractionReply(InteractionStatus.SequenceGap, false);
        }

        internal void Record(InteractionCommand command, InteractionReply reply)
        {
            _retained.Add(command.Sequence, new Receipt(command, reply));
            _order.Enqueue(command.Sequence);
            LastSequence = command.Sequence;
            if (_order.Count > _capacity) _retained.Remove(_order.Dequeue());
        }

        internal void Clear()
        {
            _retained.Clear();
            _order.Clear();
            // Disconnect is terminal for this connection: never reset/reuse its sequence identity.
        }

        private sealed class Receipt
        {
            internal Receipt(InteractionCommand command, InteractionReply reply) { Command = command; Reply = reply; }
            internal InteractionCommand Command { get; }
            internal InteractionReply Reply { get; }
        }
    }
}
