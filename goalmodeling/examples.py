"""
Some examples using the goal modeling library.
Author(s): ateeq@cmu.edu

2024-08-03: Initial version; AS.
"""

import argparse
from .schema import *


def obstacles():
    # three em dash: #11835;

    not_g1 = Obstacle("<b>not</b> G1")
    not_g2 = Obstacle("<b>not</b> G2")
    not_g = Obstacle("<b>not</b> G", [Refinement(
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
    fast_run_to_next_block_if_gosignal = SoftGoal("FastRunToNextBlock <b>If</b> GoSignal", None, None)

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
        "TrainStoppedAtBlockEntry <b>If</b> StopSignal",
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
        "DoorStateClosed <b>If</b> NonZeroMeasuredSpeed",
        [PerformanceLink(train_controller_agent, None)],
        None,
        leaf=True)

    doors_actuator = Agent("DoorsActuator", AgentType.ENVIRONMENT_AGENT)
    doorsclosed_iff_doorstateclosed = SoftGoal(
        "DoorsClosed <b>Iff</b> DoorStateClosed",
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
        "Moving <b>Iff</b> NonZeroSpeed",
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
    achieve_copyborrowed_if_available = AchieveGoal("CopyBorrowed <b>If</b> Available", None, None)
    achieve_copyduesoonforcheckout_if_not_available = AchieveGoal(
        "CopyDueSoonForCheckOut <b>If Not</b> Available",
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


def weather_dot_com(host="https://mermaid.live"):
    agent_user0 = Agent("User", AgentType.ENVIRONMENT_AGENT, annotation="An environment agent")
    type_windows_r = Operation("Type Windows Key + R", OperationCategory.ENVIRONMENT_OPERATION)
    achieve_keyboard_input_windows_r = AchieveGoal(
        name="KeyboardInputWindowsR",
        performs=[PerformanceLink(agent_user0, type_windows_r)],
        annotation="An operation")

    achieve_opened_run_window = AchieveGoal(
        name="OpenedRunWindow",
        refinements=[
            Refinement(complete=False, children=[achieve_keyboard_input_windows_r])
        ]
    )

    keep_run_window_in_foreground = Operation(
        name="Keep Run Window In Foreground",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user1 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    maintain_run_window_in_foreground = MaintainGoal(
        name="RunWindowInForeground",
        performs=[PerformanceLink(agent_user1, keep_run_window_in_foreground)])

    # not needed for an environment agent
    # achieve_set_foreground_run_window = AchieveGoal("SetForegroundRunWindow", None, None)

    type_chrome_exe_and_return_key = Operation(
        "Type Chrome.exe and hit Return",
        OperationCategory.ENVIRONMENT_OPERATION)
    agent_user3 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_keyboard_input_chrome_exe_and_return_key = AchieveGoal(
        name="KeyboardInputChromeExeAndReturnKey",
        performs=[PerformanceLink(agent_user3, type_chrome_exe_and_return_key)])

    achieve_opened_chrome = AchieveGoal("OpenedChrome", None, [
        Refinement(
            complete=False,
            children=[
                achieve_opened_run_window,
                maintain_run_window_in_foreground,
                achieve_keyboard_input_chrome_exe_and_return_key]
        )
    ])

    achieve_opened_browser_if_not_already_open_browser = AchieveGoal(
        name="OpenedBrowser <b>If Not</b> Open",
        refinements=[
            Refinement(
                complete=False,
                children=[achieve_opened_chrome]
            )
        ])

    click_new_tab_button = Operation(
        name="Click New Tab Button",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user4 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_opened_new_browser_tab = AchieveGoal(
        name="OpenedNewBrowserTab",
        performs=[PerformanceLink(agent_user4, operation=click_new_tab_button)])

    achieve_opened_new_browser_tab_if_browser_already_open = AchieveGoal(
        name="OpenedNewBrowserTab <b>If</b> Browser With Tabs Already Open",
        refinements=[
            Refinement(
                complete=False,
                children=[achieve_opened_new_browser_tab]
            )
        ])

    achieve_opened_new_tab_in_chrome = AchieveGoal(
        name="OpenedNewTabInBrowser",
        refinements=[
            Refinement(
                complete=False,
                children=[
                    achieve_opened_browser_if_not_already_open_browser,
                    achieve_opened_new_browser_tab_if_browser_already_open]
            )
        ])

    type_weather_com_and_return_key = Operation(
        "Type weather.com and hit Return key",
        OperationCategory.ENVIRONMENT_OPERATION)
    agent_user2 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_typed_weather_dot_com = AchieveGoal(
        name="TypedWeatherDotCom",
        performs=[PerformanceLink(agent_user2, type_weather_com_and_return_key)])

    wait_for_page_to_complete_loading = Operation(
        "Wait For Page To Complete Loading",
        OperationCategory.ENVIRONMENT_OPERATION)
    agent_user5 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    maintain_page_finished_loading = MaintainGoal(
        name="PageFinishedLoading",
        performs=[PerformanceLink(agent_user5, wait_for_page_to_complete_loading)])

    achieve_navigated_to_weather_dot_com = AchieveGoal(
        name="NavigatedToWeatherDotCom",
        refinements=[
            Refinement(
                complete=False,
                children=[
                    achieve_opened_new_tab_in_chrome,
                    achieve_typed_weather_dot_com,
                    maintain_page_finished_loading
                ]
            )
        ])

    read_temperature_scale_on_page = Operation(
        name="ReadTemperatureScaleOnPage",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user6 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_got_temperature_scale_on_page = AchieveGoal(
        name="GotTemperatureScaleOnPage",
        performs=[PerformanceLink(agent_user6, read_temperature_scale_on_page)],
        refinements=None)

    change_temperature_scale_to_celsius = Operation(
        name="ChangeTemperatureScaleToCelsius",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user7 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_changed_temperature_scale_to_celsius = AchieveGoal(
        name="ChangedTemperatureScaleToCelsius",
        performs=[PerformanceLink(agent_user7, change_temperature_scale_to_celsius)],
        refinements=None)

    achieve_changed_temperature_scale_if_scale_is_not_celsius = AchieveGoal(
        name="ChangedTemperatureScale <b>If Not</b> ScaleIsCelsius",
        performs=None,
        refinements=[Refinement(
            False,
            [
                achieve_got_temperature_scale_on_page,
                achieve_changed_temperature_scale_to_celsius
            ]
        )]
    )

    achieve_found_search_city_or_zip_code_field = AchieveGoal(
        "FoundZipCodeField",
        None,
        None)

    click_search_city_or_zip_code = Operation(
        "Click Search City or Zip Code",
        OperationCategory.ENVIRONMENT_OPERATION)
    agent_user8 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_search_city_or_zip_code = AchieveGoal(
        "ClickedSearchCityOrZipCode",
        [PerformanceLink(agent_user8, click_search_city_or_zip_code)],
        None)

    type_zipcode_and_hit_return = Operation(
        name="Type Zip Code and Hit Return",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user6 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_typed_zip_code_and_hit_return = AchieveGoal(
        name="TypedZipCodeAndHitReturn",
        performs=[PerformanceLink(agent_user6, type_zipcode_and_hit_return)])

    achieve_changed_zip_code_to_22206 = AchieveGoal(
        name="ChangedZipCodeTo22206",
        refinements=[
            Refinement(
                complete=False,
                children=[
                    achieve_found_search_city_or_zip_code_field,
                    achieve_clicked_search_city_or_zip_code,
                    achieve_typed_zip_code_and_hit_return,
                ]
            )
        ]
    )

    clicked_today = Operation(
        name="Click Today",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    agent_user9 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_today = AchieveGoal(
        name="ClickedToday",
        performs=[PerformanceLink(agent_user9, clicked_today)])



    achieve_got_todays_weather_in_celsius_for_zip_22206 = AchieveGoal(
        name="GotTodaysWeatherInCelsiusForZip22206",
        refinements=[
            Refinement(
                complete=False,
                children=[
                    achieve_navigated_to_weather_dot_com,
                    achieve_changed_temperature_scale_if_scale_is_not_celsius,
                    achieve_changed_zip_code_to_22206,
                    achieve_clicked_today
                ]
            )
        ]
    )

    output = generate_graph([achieve_got_todays_weather_in_celsius_for_zip_22206], [])
    link = generate_pako_link(output, mode="edit", host=host)

    print(output)
    print()
    print(link)
    # done


def pay_electric_bill(host="https://mermaid.live"):

    download_dominion_energy_application = Operation(
        name="Download Dominion Energy Application",
        category=OperationCategory.ENVIRONMENT_OPERATION)

    actor0 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_downloaded_dominion_energy_application = AchieveGoal(
        name="DownloadedDominionEnergyApplication *If* NotAlreadyInstalled",
        performs=[PerformanceLink(actor0, download_dominion_energy_application)]
    )

    click_dominion_energy_application = Operation(
        name="Click Dominion Energy Application",
        category=OperationCategory.ENVIRONMENT_OPERATION)

    actor1 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_clicked_dominion_energy_application = AchieveGoal(
        name="ClickedDominionEnergyApplication",
        performs=[PerformanceLink(actor1, click_dominion_energy_application)]
    )

    achieve_opened_dominion_energy_application = AchieveGoal(name="OpenedDominionEnergyApplication", refinements=[Refinement(
        complete=False,
        children=[achieve_downloaded_dominion_energy_application,
                  achieve_clicked_dominion_energy_application]
    )])

    click_arrow_on_welcomescreen = Operation(
        name="Click Arrow On Welcome Screen",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor2 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_clicked_arrow_on_welcomescreen = AchieveGoal(
        name="ClickedLittleArrowInFilledBlueSemiCircleOnWelcomeScreen",
        performs=[PerformanceLink(actor2, click_arrow_on_welcomescreen)]
    )

    click_not_now_for_notifications = Operation(
        name="Click Not Now For Notifications",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor3 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_not_now_for_notifications = AchieveGoal(
        name="ClickedNotNowButtonOnReceiveBillNotificationsAndAccountNotificationsScreen",
        performs=[PerformanceLink(actor3, click_not_now_for_notifications)]
    )

    click_not_now_for_allow_location_service = Operation(
        name="Click Not Now For Allow Location Service",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor4 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_not_now_for_allow_location_service = AchieveGoal(
        name="ClickedNotNowButtonAllowLocationServiceToFindYourRegionOfService",
        performs=[PerformanceLink(actor4, click_not_now_for_allow_location_service)]
    )

    click_virginia_for_state = Operation(
        name="Click Virginia For State",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor5 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_virginia_for_state = AchieveGoal(
        name="ClickedVirginiaOnSelectYourStateScreen",
        performs=[PerformanceLink(actor5, click_virginia_for_state)]
    )

    achieve_configured_dominion_energy_application_if_first_time = AchieveGoal(
        name="ConfiguredDominionEnergyApplication *If* FirstTime",
        refinements=[Refinement(
            complete=False,
            children=[achieve_clicked_arrow_on_welcomescreen,
                      achieve_clicked_not_now_for_notifications,
                      achieve_clicked_not_now_for_allow_location_service,
                      achieve_clicked_virginia_for_state]
        )]
    )

    click_my_account = Operation(
        name="Click My Account",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor6 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_my_account = AchieveGoal(
        name="ClickedMyAccountButtonOnWelcomeScreen",
        performs=[PerformanceLink(actor6, click_my_account)]
    )

    input_username = Operation(
        name="Input Username",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor7 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_input_username = AchieveGoal(
        name="InputUserNameInAccountScreen",
        performs=[PerformanceLink(actor7, input_username)]
    )

    input_password = Operation(
        name="Input Password",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor8 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_input_password = AchieveGoal(
        name="InputPasswordInAccountScreen",
        performs=[PerformanceLink(actor8, input_password)]
    )

    check_rememberme = Operation(
        name="Check Remember Me Checkbox",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor9 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_checked_rememberme = AchieveGoal(
        name="CheckedRememberMeCheckboxInAccountScreen",
        performs=[PerformanceLink(actor9, check_rememberme)]
    )

    check_enable_faceid = Operation(
        name="Check Enable FaceID Checkbox",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor10 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_checked_enable_faceid = AchieveGoal(
        name="CheckedEnableFaceIDCheckboxInAccountScreen",
        performs=[PerformanceLink(actor10, check_enable_faceid)]
    )

    achieve_email_address_for_username = AchieveGoal(name="TriedInputEmailAddressForUserNameInAccountScreen")
    obstacle_invalid_user_password = Obstacle(
        name="InvalidUserNameOrPassword",
        refinements=[Refinement(
            complete=False,
            children=[achieve_email_address_for_username]
        )]
    )

    click_login = Operation(
        name="Click Login",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor11 = Agent("User", AgentType.ENVIRONMENT_AGENT)

    achieve_clicked_login = AchieveGoal(
        name="ClickedLoginButtonInAccountScreen",
        performs=[PerformanceLink(actor11, click_login)],
        refinements=[
            Refinement(
                complete=False,
                children=[obstacle_invalid_user_password]
            )
        ]
    )

    click_ok = Operation(
        name="Click OK",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor12 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_ok = AchieveGoal(
        name="ClickedOKInAllowDominionEnergyToUseFaceIDDialog",
        performs=[PerformanceLink(actor12, click_ok)]
    )

    achieve_logged_into_account_in_dominion_energy_application_first_time = AchieveGoal(
        name="LoggedIntoAccountFirstTime",
        refinements=[Refinement(
            complete=False,
            children=[
                achieve_input_username,
                achieve_input_password,
                achieve_checked_rememberme,
                achieve_checked_enable_faceid,
                achieve_clicked_login,
                achieve_clicked_ok]
        )]
    )

    perform_face_id_login = Operation(
        name="Perform FaceID Login",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor13 = Agent("iPhone", AgentType.ENVIRONMENT_AGENT)
    achieve_performed_face_id_login = AchieveGoal(
        name="PerformedFaceIDLogin",
        performs=[PerformanceLink(actor13, perform_face_id_login)]
    )

    achieve_logged_into_account_in_dominion_energy_application = AchieveGoal(
        name="LoggedIntoAccount",
        refinements=[
            Refinement(
                complete=True,
                children=[
                    achieve_logged_into_account_in_dominion_energy_application_first_time
                ]),
            Refinement(
                complete=True,
                children=[achieve_performed_face_id_login]
            )
        ]
    )

    achieve_navigated_to_my_account_screen = AchieveGoal(
        name="NavigatedToMyAccountScreen",
        refinements=[Refinement(
            complete=True,
            children=[
                achieve_configured_dominion_energy_application_if_first_time,
                achieve_clicked_my_account,
                achieve_logged_into_account_in_dominion_energy_application]
        )]
    )

    read_current_balance = Operation(
        name="Read Current Balance",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor14 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_received_current_balance = AchieveGoal(
        name="ReceivedCurrentBalance",
        performs=[PerformanceLink(actor14, read_current_balance)]
    )

    read_next_payment_and_duedate = Operation(
        name="Read Next Payment and Due Date",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor15 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_received_next_payment_and_duedate = AchieveGoal(
        name="ReceivedNextPaymentAndDueDate",
        performs=[PerformanceLink(actor15, read_next_payment_and_duedate)]
    )

    click_make_a_payment_button = Operation(
        name="Click Make A Payment Button",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor16 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_make_a_payment_button = AchieveGoal(
        name="ClickedMakeAPaymentButton",
        performs=[PerformanceLink(actor16, click_make_a_payment_button)]
    )

    click_radio_button_for_bank_account = Operation(
        name="Click Radio Button For Bank Account",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor17 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_radio_button_for_bank_account = AchieveGoal(
        name="ClickedRadioButtonForBankAccount",
        performs=[PerformanceLink(actor17, click_radio_button_for_bank_account)]
    )

    click_next_button_in_first_payment_screen = Operation(
        name="Click Next Button In First Payment Screen",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor18 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_next_button_in_first_payment_screen = AchieveGoal(
        name="ClickedNextButton",
        performs=[PerformanceLink(actor18, click_next_button_in_first_payment_screen)]
    )

    click_total_amount_due = Operation(
        name="Click Total Amount Due",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor19 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_total_amount_due = AchieveGoal(
        name="ClickedTotalAmountDue",
        performs=[PerformanceLink(actor19, click_total_amount_due)]
    )

    click_next_button_in_second_payment_screen = Operation(
        name="Click Next Button In Second Payment Screen",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor20 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_next_button_in_second_payment_screen = AchieveGoal(
        name="ClickedNextButton",
        performs=[PerformanceLink(actor20, click_next_button_in_second_payment_screen)]
    )

    click_payment_date_now = Operation(
        name="Click Payment Date Now",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor21 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_payment_date_now = AchieveGoal(
        name="ClickedRadioButtonForPaymentDateOfNow",
        performs=[PerformanceLink(actor21, click_payment_date_now)]
    )

    click_continue = Operation(
        name="Click Continue",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor22 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_continue = AchieveGoal(
        name="ClickedContinueInWalletScreen",
        performs=[PerformanceLink(actor22, click_continue)]
    )

    click_checkbox_to_read_terms_and_conditions = Operation(
        name="Click Checkbox To Read The Terms And Conditions",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor23 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_checked_read_terms_and_conditions = AchieveGoal(
        name="ClickedCheckboxToReadTheTermsAndConditions",
        performs=[PerformanceLink(actor23, click_checkbox_to_read_terms_and_conditions)]
    )

    click_pay_amount_due_button = Operation(
        name="Click Pay Amount Due Button",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor24 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_pay_amount_due_button = AchieveGoal(
        name="ClickedPayAmountButton",
        performs=[PerformanceLink(actor24, click_pay_amount_due_button)]
    )

    read_payment_accepted = Operation(
        name="Read Payment Accepted",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor25 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_payment_accepted = AchieveGoal(
        name="AchievedPaymentAccepted",
        performs=[PerformanceLink(actor25, read_payment_accepted)]
    )

    read_confirmation_number = Operation(
        name="Read Confirmation Number",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor26 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_received_confirmation_number = AchieveGoal(
        name="ReceivedConfirmationNumber",
        performs=[PerformanceLink(actor26, read_confirmation_number)]
    )

    obstacle_print_does_not_work = Obstacle(name="PrintDoesNotWork")  # TODO

    achieve_clicked_print_button = AchieveGoal(
        name="ClickedPrintButton",
        refinements=[Refinement(
            complete=False,
            children=[obstacle_print_does_not_work]
        )]
    )

    click_done = Operation(
        name="Click Done",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor27 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_clicked_done_on_payment_confirmation_screen = AchieveGoal(
        name="ClickedDoneButton",
        performs=[PerformanceLink(actor27, click_done)]
    )

    achieve_paid_current_balance = AchieveGoal(name="PaidCurrentBalance", refinements=[Refinement(
        complete=False,
        children=[achieve_received_current_balance,
                  achieve_received_next_payment_and_duedate,
                  achieve_clicked_make_a_payment_button,
                  achieve_clicked_radio_button_for_bank_account,
                  achieve_clicked_next_button_in_first_payment_screen,
                  achieve_clicked_total_amount_due,
                  achieve_clicked_next_button_in_second_payment_screen,
                  achieve_clicked_payment_date_now,
                  achieve_clicked_continue,
                  achieve_checked_read_terms_and_conditions,
                  achieve_clicked_pay_amount_due_button,
                  achieve_payment_accepted]
    )])

    achieve_save_payment_confirmation = AchieveGoal(
        name="SavedPaymentConfirmation",
        refinements=[Refinement(
            complete=False,
            children=[achieve_received_confirmation_number,
                      achieve_clicked_print_button,
                      achieve_clicked_done_on_payment_confirmation_screen]
        )])

    read_zero_balance = Operation(
        name="Read Zero Balance",
        category=OperationCategory.ENVIRONMENT_OPERATION)
    actor28 = Agent("User", AgentType.ENVIRONMENT_AGENT)
    achieve_viewed_zero_balance = AchieveGoal(
        name="ViewedBalanceOfZero",
        performs=[PerformanceLink(actor28, read_zero_balance)]
    )

    achieve_paid_current_balance_and_saved_confirmation = AchieveGoal(
        name="PaidCurrentBalanceAndSavedConfirmation",
        refinements=[Refinement(
            complete=False,
            children=[
                achieve_paid_current_balance,
                achieve_save_payment_confirmation,
                achieve_viewed_zero_balance]
        )]
    )



    achieved_paid_with_dominion_energy_phone_app = AchieveGoal(
        name="PaidWithPhoneApp",
        refinements=[
            Refinement(
                complete=True,
                children=[
                    achieve_opened_dominion_energy_application,
                    achieve_navigated_to_my_account_screen,
                    achieve_paid_current_balance_and_saved_confirmation]
        )]
    )

    achieve_paid_dominion_energy = AchieveGoal(
        name="PaidDominionEnergy",
        refinements=[Refinement(
            complete=False,
            children=[
                achieved_paid_with_dominion_energy_phone_app])
        ]
    )

    achieve_paid_electricserviceprovider = AchieveGoal(
        name="PaidElectricServiceProvider",
        refinements=[
            Refinement(
                complete=False,
                children=[achieve_paid_dominion_energy]
            )
        ]
    )

    achieve_paid_my_electric_bill = AchieveGoal(
        name="PaidMyElectricBill",
        refinements=[
            Refinement(
                complete=False,
                children=[achieve_paid_electricserviceprovider]
            )]
    )

    output = generate_graph([achieve_paid_my_electric_bill], [])
    link = generate_pako_link(output, mode="edit", host=host)

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
