(set-logic LIA)

( declare-const hi Int )
( declare-const hi! Int )
( declare-const lo Int )
( declare-const lo! Int )
( declare-const mid Int )
( declare-const mid! Int )

( declare-const hi_0 Int )
( declare-const hi_1 Int )
( declare-const hi_2 Int )
( declare-const lo_0 Int )
( declare-const lo_1 Int )
( declare-const lo_2 Int )
( declare-const mid_0 Int )
( declare-const mid_1 Int )
( declare-const mid_2 Int )

( define-fun inv-f( ( hi Int )( lo Int )( mid Int ) ) Bool
SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop
)

( define-fun pre-f ( ( hi Int )( lo Int )( mid Int )( hi_0 Int )( hi_1 Int )( hi_2 Int )( lo_0 Int )( lo_1 Int )( lo_2 Int )( mid_0 Int )( mid_1 Int )( mid_2 Int ) ) Bool
        ( and
                ( = hi hi_0 )
                ( = lo lo_0 )
                ( = mid mid_0 )
                ( > mid_0 0 )
                ( = lo_0 0 )
                ( = hi_0 ( * 2 mid_0 ) )
        )
)

( define-fun trans-f ( ( hi Int )( lo Int )( mid Int )( hi! Int )( lo! Int )( mid! Int )( hi_0 Int )( hi_1 Int )( hi_2 Int )( lo_0 Int )( lo_1 Int )( lo_2 Int )( mid_0 Int )( mid_1 Int )( mid_2 Int ) ) Bool
        ( or
                ( and
                        ( = hi_1 hi )
                        ( = lo_1 lo )
                        ( = mid_1 mid )
                        ( = hi_1 hi! )
                        ( = lo_1 lo! )
                        ( = mid_1 mid! )
                        ( = hi hi! )
                        ( = lo lo! )
                )
                ( and
                        ( = hi_1 hi )
                        ( = lo_1 lo )
                        ( = mid_1 mid )
                        ( > mid_1 0 )
                        ( = lo_2 ( + lo_1 1 ) )
                        ( = hi_2 ( - hi_1 1 ) )
                        ( = mid_2 ( - mid_1 1 ) )
                        ( = hi_2 hi! )
                        ( = lo_2 lo! )
                        ( = mid_2 mid! )
                )
        )
)

( define-fun post-f ( ( hi Int )( lo Int )( mid Int )( hi_0 Int )( hi_1 Int )( hi_2 Int )( lo_0 Int )( lo_1 Int )( lo_2 Int )( mid_0 Int )( mid_1 Int )( mid_2 Int ) ) Bool
        ( or
                ( not
                        ( and
                                ( = hi hi_1)
                                ( = lo lo_1)
                                ( = mid mid_1)
                        )
                )
                ( not
                        ( and
                                ( not ( > mid_1 0 ) )
                                ( not ( = lo_1 hi_1 ) )
                        )
                )
        )
)
SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop
( assert ( not
        ( =>
                ( pre-f hi lo mid hi_0 hi_1 hi_2 lo_0 lo_1 lo_2 mid_0 mid_1 mid_2  )
                ( inv-f hi lo mid )
        )
))

SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop
( assert ( not
        ( =>
                ( and
                        ( inv-f hi lo mid )
                        ( trans-f hi lo mid hi! lo! mid! hi_0 hi_1 hi_2 lo_0 lo_1 lo_2 mid_0 mid_1 mid_2 )
                )
                ( inv-f hi! lo! mid! )
        )
))

SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop
( assert ( not
        ( =>
                ( inv-f hi lo mid  )
                ( post-f hi lo mid hi_0 hi_1 hi_2 lo_0 lo_1 lo_2 mid_0 mid_1 mid_2 )
        )
))