"""
Some examples using the goal modeling library.
Author(s): ateeq@cmu.edu

2024-08-03: Initial version; AS.
"""

import argparse
from .schema import *


def obstacles():
    # three em dash: #11835;

    not_g1 = Obstacle("**not** G1")
    not_g2 = Obstacle("**not** G2")
    not_g = Obstacle("**not** G", [Refinement(
        False,
        [not_g1]),
        Refinement(
        False,
        [not_g2])])

    g1 = SoftGoal("G1")
    g2 = SoftGoal("G2")
    g = SoftGoal("G", None, [
        Refinement(False, [g1, g2])
    ])

    g1_not_g1 = ObstructionLink(g1, not_g1)
    g2_not_g2 = ObstructionLink(g2, not_g2)

    output = generate_graph([g, not_g], [g1_not_g1, g2_not_g2])

    print(output)
    print(generate_pako_link(output))
    print()


def conflicts():
    signal_promptly_set_go = SoftGoal("SignalPromptlySetGo", None, None)
    fast_run_to_next_block_if_gosignal = SoftGoal("FastRunToNextBlock **If** GoSignal", None, None)

    fast_journey = SoftGoal(
        "FastJourney",
        None,
        [Refinement(
            complete=False,
            children=[signal_promptly_set_go, fast_run_to_next_block_if_gosignal])])

    rapid_transportation = SoftGoal(
        "RapidTransportation",
        None,
        [Refinement(
            complete=False,
            children=[fast_journey])])

    signalsafelykepttostop = SoftGoal("SignalSafelyKeptToStop", None, None)
    train_stoppedatblockentry_if_stopsignal = SoftGoal(
        "TrainStoppedAtBlockEntry **If** StopSignal",
        None,
        None)
    avoid_trainonsameblock = AvoidGoal(
        name="AvoidTrainOnSameBlock",
        performs=None,
        refinements=[Refinement(
            complete=False,
            children=[signalsafelykepttostop, train_stoppedatblockentry_if_stopsignal])])

    avoid_traincollisions = AvoidGoal(
        name="AvoidTrainCollisions",
        performs=None,
        refinements=[Refinement(
            complete=False,
            children=[avoid_trainonsameblock]
        )])

    safe_transportation = SoftGoal(
        "SafeTransportation",
        None,
        [Refinement(
            complete=False,
            children=[avoid_traincollisions])])
    effective_passengers_transportation = SoftGoal(
        "EffectivePassengersTransportation",
        None,
        [Refinement(
            complete=False,
            children=[rapid_transportation, safe_transportation])])

    conflict_signalsafelykepttostop_and_signalpromptlysetgo = ConflictLink(signalsafelykepttostop,
                                                                           signal_promptly_set_go)

    output = diagram_startup()
    output += effective_passengers_transportation.to_tree()
    output += conflict_signalsafelykepttostop_and_signalpromptlysetgo.to_string()
    output += diagram_teardown()

    output = generate_graph(
        [effective_passengers_transportation],
        [conflict_signalsafelykepttostop_and_signalpromptlysetgo])

    link = generate_pako_link(output)
    print(output)
    print()
    print(link)


def actors():
    speed_sensor_agent = Agent(
        "SpeedSensor",
        AgentType.ENVIRONMENT_AGENT,
        annotation="environment agent")
    measure_speed_equals_physical_speed = SoftGoal(
        name="MeasureSpeed=PhysicalSpeed",
        performs=[PerformanceLink(
            speed_sensor_agent,
            Operation(
                "MeasureSpeed",
                OperationCategory.ENVIRONMENT_OPERATION))],
        refinements=None,
        leaf=True,
        annotation="expectation")

    train_controller_agent = Agent("TrainController", AgentType.SOFTWARE_AGENT)
    maintain_doors_closed_if_nonzero_measured_speed = MaintainGoal(
        "DoorStateClosed **If** NonZeroMeasuredSpeed",
        [PerformanceLink(train_controller_agent, None)],
        None,
        leaf=True)

    doors_actuator = Agent("DoorsActuator", AgentType.ENVIRONMENT_AGENT)
    doorsclosed_iff_doorstateclosed = SoftGoal(
        "DoorsClosed **Iff** DoorStateClosed",
        [PerformanceLink(doors_actuator, None)],
        None,
        leaf=True)

    maintain_doors_closed_while_nonzero_speed = MaintainGoal(
        "DoorsClosedWhileNonZeroSpeed",
        None,
        [Refinement(
            complete=True,
            children=[measure_speed_equals_physical_speed,
                      maintain_doors_closed_if_nonzero_measured_speed,
                      doorsclosed_iff_doorstateclosed
                      ])]
    )

    moving_iff_nonzero_speed = DomainProperty(
        "Moving **Iff** NonZeroSpeed",
        leaf=True,
        annotation="domain property")

    maintain_doors_closed_while_moving = MaintainGoal(
        "DoorsClosedWhileMoving",
        None,
        [Refinement(
            False,
            [moving_iff_nonzero_speed, maintain_doors_closed_while_nonzero_speed])]
    )


    output = generate_graph([maintain_doors_closed_while_moving], [])
    link = generate_pako_link(output)
    print(output)
    print()
    print(link)


def achievement():
    achieve_copyborrowed_if_available = AchieveGoal("CopyBorrowed **If** Available", None, None)
    achieve_copyduesoonforcheckout_if_not_available = AchieveGoal(
        "CopyDueSoonForCheckOut **If Not** Available",
        None,
        None)
    achieve_book_request_satisfied = AchieveGoal(
        "BookRequestSatisfied",
        None,
        [Refinement(
            False,
            [
                achieve_copyborrowed_if_available,
                achieve_copyduesoonforcheckout_if_not_available]
        )])


    output = generate_graph([achieve_book_request_satisfied], [])
    link = generate_pako_link(output)

    print(output)
    print()
    print(link)


def main():
    parser = argparse.ArgumentParser(
        prog='examples',
        description="Goal refinement graph examples.",
        epilog=""
    )

    parser.add_argument(
        "--figure8.2",
        action="store_true",
        dest="figure8_2",
        help="Generate Figure 8.2")
    parser.add_argument(
        "--figure8.4",
        action="store_true",
        dest="figure8_4",
        help="Generate Figure 8.4")
    parser.add_argument(
        "--figure8.7",
        action="store_true",
        dest="figure8_7",
        help="Generate Figure 8.7")
    parser.add_argument(
        "--figure9.5",
        action="store_true",
        dest="figure9_5",
        help="Generate Figure 9.5")

    args = parser.parse_args()

    if args.figure8_2:
        achievement()
    if args.figure8_4:
        actors()
    if args.figure8_7:
        conflicts()
    if args.figure9_5:
        obstacles()


if __name__ == "__main__":
    main()